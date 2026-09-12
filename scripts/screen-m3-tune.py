#!/usr/bin/env python3
"""Two-TU Apple backend screen, old O2+PGO versus ISA-preserving M3 tuning.

Requires --execute to compile. Retained single-TU ThinLTO links are not playable
modules or full-module performance proof. Canonical files are never changed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'generated/build/ios-simulator-pgo-use-20260912'
PROFILE = ROOT/'generated/runtime/ipad-iteration-1/pgo-profile-route-20260912/current-input.profdata'
BASE_SHA = '90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f'
PROF_SHA = '784f47e4904a36319b7805cd7807091d1d486ccc4cacc09f4785636d3949ca54'
CHUNKS = ['804B60A0', '805170A0']


def require(ok, reason):
    if not ok:
        raise SystemExit(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv, log):
    start = time.monotonic()
    p = subprocess.run(argv, capture_output=True, text=True, timeout=180)
    output = p.stdout+p.stderr
    log.write_text(output)
    require(p.returncode == 0, f'Command failed: {log}')
    require(not re.search(r'warning:.*(?:profile|profdata)|error:', output, re.I),
            f'Unexpected diagnostic: {log}')
    print(log.name, f'{time.monotonic()-start:.2f}s', flush=True)
    return output


def normalized_object_dump(raw):
    # Apple linker's saved native Mach-O object keeps unresolved operands plus
    # inline symbolic relocation records. Remove only file identity, whitespace,
    # and instruction/label addresses; retain all operands and relocation names.
    rows = []
    for line in raw.splitlines():
        if not line.strip() or 'file format mach-o' in line:
            continue
        line = re.sub(r'^\s*[0-9a-f]+\s+(?=<)', '', line)
        line = re.sub(r'^\s*[0-9a-f]+:\s*', '', line)
        rows.append(' '.join(line.split()))
    return '\n'.join(rows)+'\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    args = p.parse_args()
    out = args.output.resolve()
    require(sha(BUILD/'gRMGE01_recomp.dylib') == BASE_SHA, 'Control module changed')
    require(sha(PROFILE) == PROF_SHA, 'Old profile changed')
    rows = json.loads((BUILD/'compile_commands.json').read_text())
    linkline = subprocess.check_output(['ninja','-C',str(BUILD),'-t','commands','gRMGE01_recomp.dylib'],text=True).splitlines()[-1]
    link = shlex.split(linkline)
    require(link[:2] == [':','&&'] and link[-2:] == ['&&',':'], 'Unexpected link wrapper')
    link = [x for x in link[2:-2] if not x.endswith('.o')]
    require('-O3' in link and '-O2' not in link and '-flto=thin' in link, 'Unexpected LTO policy')
    require(not out.exists(), 'Output exists; preserve prior evidence')
    out.mkdir(parents=True)
    plan = {'status':'prepared', 'baseline_sha256':BASE_SHA, 'profile_sha256':PROF_SHA, 'chunks':{}}
    for chunk in CHUNKS:
        row = next(r for r in rows if chunk+'.c' in r['file'])
        base = shlex.split(row['command'])
        require(base.count('-O2') == 1 and '-flto=thin' in base and
                '-fprofile-instr-use='+str(PROFILE) in base, 'Unexpected compile policy')
        plan['chunks'][chunk] = {'source':row['file'],'source_sha256':sha(Path(row['file'])), 'variants':{}}
        for variant,extra in [('control',[]),('m3',['-mtune=apple-m3'])]:
            prefix = out/(chunk+'-'+variant)
            compile_cmd = base+extra
            compile_cmd[compile_cmd.index('-o')+1] = str(prefix.with_suffix('.bc'))
            # Read optimized bitcode without rerunning source/frontend passes.
            ir_cmd = [base[0],'-cc1','-triple','arm64-apple-ios16.0.0-simulator',
                      '-emit-llvm','-disable-llvm-passes','-x','ir',str(prefix.with_suffix('.bc')),
                      '-o',str(prefix.with_suffix('.ll'))]
            link_cmd = link+extra+['-Wl,-u,_func_'+chunk,'-Wl,-undefined,dynamic_lookup',
                                 '-Wl,-object_path_lto,'+str(prefix.with_suffix('.native.o')),
                                 str(prefix.with_suffix('.bc'))]
            link_cmd[link_cmd.index('-o')+1] = str(prefix.with_suffix('.dylib'))
            # Keep install name identical to the original link on both sides.
            plan['chunks'][chunk]['variants'][variant] = {'compile':compile_cmd,'ir':ir_cmd,'link':link_cmd}
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    if not args.execute:
        print('Prepared only; rerun --execute with a fresh output directory after resource release.')
        return
    results = {}
    for chunk,entry in plan['chunks'].items():
        results[chunk] = {}
        for variant,commands in entry['variants'].items():
            prefix = out/(chunk+'-'+variant)
            for stage in ['compile','ir','link']:
                run(commands[stage],Path(str(prefix)+'-'+stage+'.log'))
            ir = prefix.with_suffix('.ll').read_text()
            metadata = {key:sorted(set(re.findall('"'+key+'"="([^"]+)"',ir)))
                        for key in ['target-cpu','target-features','tune-cpu']}
            require(metadata['target-cpu'] == ['apple-m1'], 'ISA target-cpu changed')
            require(metadata['tune-cpu'] == ([] if variant=='control' else ['apple-m3']), 'Unexpected tune metadata')
            native = prefix.with_suffix('.native.o')
            if native.is_dir():
                objects = list(native.rglob('*.o'))
                require(len(objects)==1, 'Unexpected number of saved LTO native objects')
                native = objects[0]
            require(native.is_file(), 'Apple linker did not save its native LTO object')
            dump = run(['xcrun','llvm-objdump','-dr','--no-show-raw-insn','--symbolize-operands',str(native)],
                       Path(str(prefix)+'-native.asm'))
            normalized = normalized_object_dump(dump)
            Path(str(prefix)+'-normalized.asm').write_text(normalized)
            linked = run(['xcrun','llvm-objdump','--disassemble-symbols=_func_'+chunk,
                          str(prefix.with_suffix('.dylib'))],Path(str(prefix)+'-linked.asm'))
            instructions = re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\S+)',linked,re.M)
            require(len(instructions)>100, 'Retained linked chunk is absent or unexpectedly small')
            results[chunk][variant] = {'metadata':metadata,'normalized_sha256':hashlib.sha256(normalized.encode()).hexdigest(),
                                      'linked_instruction_count':len(instructions),'linked_opcodes':dict(Counter(instructions))}
        a,b=results[chunk]['control'],results[chunk]['m3']
        require(a['metadata']['target-features']==b['metadata']['target-features'], 'ISA feature list changed')
        results[chunk]['relocation_normalized_identical'] = a['normalized_sha256']==b['normalized_sha256']
        encodings = [re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s+',
                     (out/(chunk+'-'+v+'-linked.asm')).read_text(), re.M)
                     for v in ['control','m3']]
        results[chunk]['linked_raw_instruction_bytes_identical'] = encodings[0] == encodings[1]
        require(sha(Path(entry['source']))==entry['source_sha256'], 'Source changed during screen')
    identical = all(x['relocation_normalized_identical'] for x in results.values())
    summary = {'chunks':results,'decision':'reject identical codegen' if identical else 'inspect code differences before any full build',
               'scope':'two isolated native ThinLTO outputs; not full module or FPS evidence'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
