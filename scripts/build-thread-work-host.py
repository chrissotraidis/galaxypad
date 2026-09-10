#!/usr/bin/env python3
"""Isolated Apple host diagnostic; verify unchanged cache before replacement."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import struct

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--native',action='store_true',help='Use the R730 native runner/cache')
parser.add_argument('--sample-capacity',type=int,choices=(16384,65536),default=16384,
                    help='Paired private recorder capacity; ordinary host remains unchanged')
parser.add_argument('--background-input-option',action='store_true',
                    help='Native only: add default-off automation option to private runner')
args=parser.parse_args(); out=args.output.resolve()
if args.background_input_option and not args.native:
    parser.error('--background-input-option requires --native')
out.mkdir(parents=True,exist_ok=False)
build=root/'generated/build/ios-simulator-thp-app'
corebuild=root/'generated/build/ios-simulator-core'
core=root/'generated/ios/iphonesimulator/libs/libGalaxyPadCore.a'
baseline=build/'GalaxyPad.app/GalaxyPad'
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
app_source=build/'GalaxyPad.app'; executable_relative=Path('GalaxyPad')
link_target='GalaxyPad.app/GalaxyPad'
expected='85ffc10065d375062a0c445d87d0a501d4fc91e236986d6d55d74f0b8333dbcc'
if args.native:
    build=corebuild=root/'generated/build/moderngekko-desktop'
    core=build/'libmoderngekko.a'
    app_source=root/'generated/macos/direct-calls-r730/GalaxyPad.app'
    executable_relative=Path('Contents/MacOS/GalaxyPadRunner')
    baseline=app_source/executable_relative; link_target='moderngekko-run'
    expected='871f4f8726cf1e12c56022a61dfbd013cbfa6614ce68ee6873982e869a9f4faf'
assert sha(baseline)==expected
member='dolphin_runtime.cpp.o'
members=subprocess.check_output(['ar','-t',str(core)],text=True).splitlines()
assert members.count(member)==1
original=subprocess.check_output(['ar','-p',str(core),member])
commands=json.loads((corebuild/'compile_commands.json').read_text())
rows=[r for r in commands if r['file'].endswith('/runtime/dolphin_runtime.cpp')]
if args.native and not rows:
    # Desktop compile_commands is stale/incomplete; query the actual object rule.
    target='CMakeFiles/moderngekko.dir/src/runtime/dolphin_runtime.cpp.o'
    raw_compile=subprocess.check_output(['ninja','-t','commands',target],cwd=corebuild,text=True).splitlines()[-1]
    tokens=shlex.split(raw_compile)
    assert not any(x in ('&&',';','|') for x in tokens)
    # Do not overwrite cached dependency files while compiling the private copy.
    for option in ('-MT','-MF'):
        assert tokens.count(option)==1
        index=tokens.index(option); del tokens[index:index+2]
    assert tokens.count('-MD')==1; tokens.remove('-MD')
    source=str(root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp')
    assert tokens[-2:]==['-c',source]
    rows=[dict(file=source,command=shlex.join(tokens))]
assert len(rows)==1
row=rows[0]; command=shlex.split(row['command'])
assert command.count('-o')==1 and command.count('-c')==1
manifest={'baseline':sha(baseline),'core':sha(core),
          'runtime_source':sha(row['file']),'archived_object':hashlib.sha256(original).hexdigest()}
def record(): (out/'provenance.json').write_text(json.dumps(manifest,indent=2))
record()
control=out/'control'; control.mkdir()
compile_control=command.copy(); compile_control[compile_control.index('-o')+1]=str(control/member)
manifest['control_compile']=compile_control; record()
print('Compile unchanged runtime object to verify cache identity',flush=True)
subprocess.run(compile_control,cwd=corebuild,check=True)
manifest['control_object']=sha(control/member); record()
assert (control/member).read_bytes()==original, 'Current source/flags do not reproduce archived runtime; stop before candidate'

raw=subprocess.check_output(['ninja','-t','commands',link_target],cwd=build,text=True).splitlines()[-1]
tokens=shlex.split(raw)
if args.native:
    suffix=['&&','cd',str(build),'&&','/opt/homebrew/bin/cmake','-E','copy_directory',
            str(root/'ref/ModernGekko/vendor/dolphin/Data/Sys'),str(build/'Sys')]
    assert tokens[-len(suffix):]==suffix
    # Packaged baseline already contains Sys. Never execute this cache mutation.
    tokens=tokens[:-len(suffix)]+['&&',':']
assert tokens[:2]==[':','&&'] and tokens[-2:]==['&&',':']
link=tokens[2:-2]; assert not any(x in ('&&',';','|') for x in link)
if args.native:
    assert link.count('libmoderngekko.a')==1
    link[link.index('libmoderngekko.a')]=str(core)
assert link.count('-o')==1 and link.count(str(core))==1
control_executable=control/('moderngekko-run' if args.native else 'GalaxyPad')
control_link=link.copy(); control_link[control_link.index('-o')+1]=str(control_executable)
manifest['control_link']=control_link; record()
print('Relink unchanged host and compare after stripping only signatures',flush=True)
subprocess.run(control_link,cwd=build,check=True)
for name,source in [('baseline-unsigned',baseline),('control-unsigned',control_executable)]:
    shutil.copyfile(source,out/name)
    subprocess.run(['codesign','--remove-signature',str(out/name)],check=True)
def linkedit_reservation(data, allow_uuid=False):
    # codesign removal retains its old virtual reservation even after removing
    # signature bytes. Permit only this parsed field, never arbitrary byte masks.
    b=bytearray(data)
    assert struct.unpack_from('<I',b)[0]==0xfeedfacf
    count,command_bytes=struct.unpack_from('<II',b,16)
    offset=32; found=[]; uuid_count=0
    for _ in range(count):
        cmd,size=struct.unpack_from('<II',b,offset)
        assert size>=8 and offset+size<=32+command_bytes
        if cmd==0x1b:
            assert size==24
            uuid_count+=1
            if allow_uuid: b[offset+8:offset+24]=bytes(16)
        if cmd==0x19 and b[offset+8:offset+24].rstrip(b'\0')==b'__LINKEDIT':
            assert size==72
            vm_size=struct.unpack_from('<Q',b,offset+32)[0]
            file_size=struct.unpack_from('<Q',b,offset+48)[0]
            maxprot,initprot,nsects=struct.unpack_from('<III',b,offset+56)
            assert vm_size>=file_size and vm_size%16384==0
            assert maxprot==initprot==1 and nsects==0
            found.append((offset+32,vm_size))
            struct.pack_into('<Q',b,offset+32,0)
        offset+=size
    assert offset==32+command_bytes and len(found)==1
    if allow_uuid: assert uuid_count==1
    return bytes(b),found[0]
base_bytes,base_field=linkedit_reservation((out/'baseline-unsigned').read_bytes(),args.native)
control_bytes,control_field=linkedit_reservation((out/'control-unsigned').read_bytes(),args.native)
assert base_field[0]==control_field[0] and base_bytes==control_bytes, 'Unchanged host differs beyond explicitly allowed LINKEDIT/UUID metadata'
if args.native:
    manifest['control_uuid_metadata']=subprocess.check_output(
        ['xcrun','dwarfdump','--uuid',str(out/'baseline-unsigned'),str(out/'control-unsigned')],text=True)
manifest['control_linkedit_reservations']={'baseline':base_field,'control':control_field}
manifest['unsigned_control']=sha(out/'control-unsigned'); record()

spec=importlib.util.spec_from_file_location('overlay',root/'scripts/prepare-thread-work-recorder.py')
overlay=importlib.util.module_from_spec(spec); spec.loader.exec_module(overlay)
overlay.prepare(out/'headers',args.sample_capacity)
manifest['sample_capacity']=args.sample_capacity; record()
# Clang VFS redirects the original quoted sibling header; no vendor edit or
# source relocation. Included private header is also in explicit include path.
vfs={'version':0,'roots':[{'type':'file','name':str(root/'ref/ModernGekko/src/runtime/vi-timing-recorder.h'),
                         'external-contents':str(out/'headers/vi-timing-recorder.h')}]}
(out/'overlay.json').write_text(json.dumps(vfs))
candidate=out/'candidate'; candidate.mkdir()
compile_candidate=command.copy(); compile_candidate[compile_candidate.index('-o')+1]=str(candidate/member)
compile_candidate += ['-DGALAXYPAD_PRIVATE_THREAD_WORK=1','-ivfsoverlay',str(out/'overlay.json'),'-I'+str(out/'headers')]
manifest['candidate_compile']=compile_candidate; record()
print('Compile only private runtime object; reuse unchanged guest module and host objects',flush=True)
subprocess.run(compile_candidate,cwd=corebuild,check=True)
assert b'thread_selfcounts' in subprocess.check_output(['strings',str(candidate/member)])
privatecore=candidate/'libGalaxyPadCore.a'; shutil.copyfile(core,privatecore)
subprocess.run(['ar','r',str(privatecore),str(candidate/member)],check=True)
assert subprocess.check_output(['ar','-p',str(privatecore),member])==(candidate/member).read_bytes()
app=candidate/'GalaxyPad.app'; shutil.copytree(app_source,app)
candidate_link=link.copy(); candidate_link[candidate_link.index('-o')+1]=str(app/executable_relative)
candidate_link[candidate_link.index(str(core))]=str(privatecore)
if args.background_input_option:
    runner_target='CMakeFiles/moderngekko-run.dir/tools/moderngekko_run.cpp.o'
    runner_source=root/'ref/ModernGekko/tools/moderngekko_run.cpp'
    patch=root/'patches/experiments/runner-background-input.patch'
    assert candidate_link.count(runner_target)==1
    runner_command=shlex.split(subprocess.check_output(
        ['ninja','-t','commands',runner_target],cwd=build,text=True).splitlines()[-1])
    assert not any(x in ('&&',';','|') for x in runner_command)
    for flag in ('-MT','-MF'):
        assert runner_command.count(flag)==1
        i=runner_command.index(flag); del runner_command[i:i+2]
    assert runner_command.count('-MD')==1; runner_command.remove('-MD')
    assert runner_command[-2:]==['-c',str(runner_source)]
    assert runner_command.count('-o')==1
    runner_original=sha(build/runner_target)
    runner_control=control/'runner.o'
    runner_command[runner_command.index('-o')+1]=str(runner_control)
    manifest['runner_control_compile']=runner_command.copy(); record()
    subprocess.run(runner_command,cwd=build,check=True)
    assert sha(runner_control)==runner_original, 'Runner cache not reproducible'
    private_source=out/'runner-source'; (private_source/'tools').mkdir(parents=True)
    copied_source=private_source/'tools/moderngekko_run.cpp'
    shutil.copyfile(runner_source,copied_source)
    runner_command[runner_command.index('-c')+1]=str(copied_source)
    runner_command += ['-I'+str(runner_source.parent)]
    # Prove source relocation itself is inert before patching the private copy.
    subprocess.run(runner_command,cwd=build,check=True)
    assert sha(runner_control)==runner_original, 'Relocated unchanged runner differs'
    # git apply from an ignored subdirectory can skip root-relative patch paths.
    # patch applies relative to this explicit private source directory instead.
    subprocess.run(['patch','-p1','-i',str(patch)],cwd=private_source,check=True)
    assert 'background input explicitly enabled' in copied_source.read_text()
    runner_candidate=candidate/'runner.o'
    runner_command[runner_command.index('-o')+1]=str(runner_candidate)
    manifest.update(runner_patch=sha(patch),runner_source=sha(runner_source),
                    runner_original=runner_original,runner_candidate_compile=runner_command)
    record()
    subprocess.run(runner_command,cwd=build,check=True)
    assert b'background input explicitly enabled' in subprocess.check_output(['strings',str(runner_candidate)])
    candidate_link[candidate_link.index(runner_target)]=str(runner_candidate)
    assert sha(build/runner_target)==runner_original and sha(runner_source)==manifest['runner_source']
    manifest['runner_candidate']=sha(runner_candidate)
manifest['candidate_link']=candidate_link; record()
subprocess.run(candidate_link,cwd=build,check=True)
subprocess.run(['codesign','--force','--sign','-',str(app)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True)
assert sha(core)==manifest['core'] and sha(baseline)==manifest['baseline']
manifest.update(candidate=sha(app/executable_relative),candidate_object=sha(candidate/member),complete=True)
record(); print('Private host ready: '+str(app),flush=True)
