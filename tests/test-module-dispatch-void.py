#!/usr/bin/env python3
"""Compare the real optional void dispatcher with emitted ABI dispatch semantics."""
import ast,pathlib,re,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
import tempfile
workspace=tempfile.TemporaryDirectory(prefix='galaxypad-void-dispatch-')
out=pathlib.Path(workspace.name)
source=(root/'tests/test-module-dispatch-outline.py').read_text()
tree=ast.parse(source)
core=root/'ref/ModernGekko/vendor/dolphin'
emitter=(core/'DolRecomp/src/backend/dispatch.c').read_text()
start=emitter.index('    fprintf(out, "\\nstatic inline int dolrecomp_call_original')
end=emitter.index('    fprintf(out, "\\nstatic inline DOLRECOMP_UNUSED int dolrecomp_run_blocks',start)
body=''.join(ast.literal_eval(m) for m in re.findall(r'fprintf\(out, ("(?:[^"\\]|\\.)*")\);',emitter[start:end]))
node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='program' for t in n.targets))
while isinstance(node,ast.Call):node=node.func.value
program=ast.literal_eval(node)
module=(root/'ref/ModernGekko/vendor/dolphin/module-template/module_export.c').read_text()
void=module[module.index('RECOMP_MODULE_EXPORT void staticrecomp_dispatch_void_v1'):module.rindex('#endif')]
void=void.replace('RECOMP_MODULE_EXPORT', '')
program=program.replace('BODY',body).replace('WRAPPER',void)
program=program.replace('int actual=chassis_dispatch(&c,addresses[a]);assert(expected==actual);','staticrecomp_dispatch_void_v1(&c,addresses[a]);')
(out/'verify.c').write_text(program)
for flags in [['-O2'],['-O1','-fsanitize=address,undefined']]:
 for replacement in [0,1]:
  cmd=['clang','-std=c11',*flags,'-I',str(core/'GXRuntime/include'),str(out/'verify.c'),'-o',str(out/'verify')]
  if replacement:cmd+=['-DDOLRECOMP_ENABLE_REPLACEMENTS=1']
  subprocess.run(cmd,check=True);subprocess.run([str(out/'verify')],check=True)
