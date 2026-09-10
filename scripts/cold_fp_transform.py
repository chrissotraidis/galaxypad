"""Deterministic, source-pinned cold-exception experiment (never edits ref)."""
from pathlib import Path
import hashlib
import shutil

ORIGINAL_SHA='3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c'
def end_brace(text,start):
    depth=1;i=start+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return i

def transform(source):
    if hashlib.sha256(source.encode()).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('Unexpected float helper source identity')
    for op in ['add','sub']:
        start=source.index('FPRes ni_'+op+'(')
        brace=source.index('{',start);end=end_brace(source,brace)
        body=source[start:end]
        guard=body.index('    if (isnan(result.value)) {')
        inner=body.index('{',guard);finish=end_brace(body,inner)
        cold='__attribute__((noinline,cold)) static FPRes cold_'+op+'(CPUState* cpu,f64 a,f64 b,FPRes result) {'+body[inner+1:finish-1]+'}\n\n'
        hot=body[:guard]+'    if (isnan(result.value)) return cold_'+op+'(cpu,a,b,result);'+body[finish:]
        source=source[:start]+cold+hot+source[end:]
    return source

def prepare():
    root=Path(__file__).resolve().parents[1]
    original=root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
    experiment=root/'generated/cold-fp-r160'
    target=experiment/'GXRuntime'
    relative=Path('src/core/cpu_interpreter_float.c')
    changed=transform((original/relative).read_text())
    if not target.exists():
        shutil.copytree(original,target)
        (target/relative).write_text(changed)
    # Repeated preparation fails closed on stale/unrelated copied source edits.
    originals={p.relative_to(original) for p in original.rglob('*') if p.is_file()}
    copies={p.relative_to(target) for p in target.rglob('*') if p.is_file()}
    if originals!=copies: raise ValueError('Candidate runtime file set differs')
    for name in originals:
        expected=changed.encode() if name==relative else (original/name).read_bytes()
        if (target/name).read_bytes()!=expected: raise ValueError('Candidate mismatch: '+str(name))
    accepted=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
    if hashlib.sha256(accepted.read_bytes()).hexdigest()!='9098890e25b36e802ab5f793c9ad7800f991190f41e972996937343d84ecc9de':
        raise ValueError('Unexpected accepted module')
    module_build=experiment/'module-build';module_build.mkdir(exist_ok=True)
    manifest=(accepted.parent/'manifest.txt').read_text().replace('module_sources_fnv1a=', 'reference_module_sources_fnv1a=')
    manifest+='experiment=cold-fp-r160\nselected=false\ncandidate_float_sha256='+hashlib.sha256(changed.encode()).hexdigest()+'\n'
    (module_build/'manifest.txt').write_text(manifest)
    link=module_build/'dolrecomp-output'
    expected_link=accepted.parent/'dolrecomp-output'
    if not link.exists(): link.symlink_to(expected_link,target_is_directory=True)
    if link.resolve()!=expected_link.resolve(): raise ValueError('Unexpected generated source link')
    print('Isolated runtime verified; candidate float SHA256='+hashlib.sha256(changed.encode()).hexdigest())

if __name__=='__main__': prepare()
