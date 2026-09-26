#!/usr/bin/env python3
"""Differential-check promoted chunks against the original generated chunks."""
from pathlib import Path
import argparse, concurrent.futures as cf, json, random, re, subprocess

HERE = Path(__file__).resolve().parent
RUNTIME_SOURCES = ['cpu.c', 'cpu_exception.c', 'cpu_interpreter.c', 'cpu_interpreter_float.c',
                   'cpu_interpreter_integer.c', 'cpu_interpreter_table.c']
MODES = {'o2': ['-O2'], 'san': ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=undefined']}

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--original', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--runtime', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--chunks', nargs='*', default=[])
p.add_argument('--random', type=int, default=0)
p.add_argument('--seed', type=int, default=20260926)
p.add_argument('--trials', type=int, default=2)
p.add_argument('--jobs', type=int, default=8)
a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
inc = ['-I', str(a.original.resolve()), '-I', str(a.runtime/'GXRuntime/include'),
       '-I', str(a.runtime/'Source/Core/Core/PowerPC/StaticRecomp')]
cc = ['xcrun', 'clang', '-std=gnu11', '-ffp-contract=off', '-fno-fast-math', '-w', '-DGP_CALLBACK_CONTRACT'] + inc

def run(cmd, log):
    r = subprocess.run(cmd, text=True, capture_output=True)
    log.write(' '.join(map(str, cmd)) + '\n' + r.stdout + r.stderr)
    return r

libs = {}
with (out/'runtime.log').open('w') as log:
    for mode, flags in MODES.items():
        objs = []
        for f in RUNTIME_SOURCES:
            o = out/f'rt-{mode}-{f}.o'
            assert run(cc + flags + ['-c', str(a.runtime/'GXRuntime/src/core'/f), '-o', str(o)], log).returncode == 0
            objs.append(str(o))
        libs[mode] = objs

names = sorted(f.stem for f in (a.original/'chunks').glob('*.c'))
chosen = list(a.chunks) + random.Random(a.seed).sample([n for n in names if n not in a.chunks], a.random)

def check(name):
    d = out/name; d.mkdir()
    text = (a.original/'chunks'/(name + '.c')).read_text()
    fn = re.search(r'^void (func_[0-9A-F]+)\(CPUState\* ctx\) \{', text, re.M).group(1)
    body = text[text.index(f'void {fn}(CPUState* ctx) {{'):]
    entries = re.findall(r'case (0x[0-9A-F]+)u:', body[body.index('switch (ctx->pc) {'):body.index('default:')])
    (d/'entries.c').write_text('const unsigned gp_entries[]={%s};\nconst unsigned gp_entry_count=%d;\n' % (','.join(entries), len(entries)))
    result = {'entries': len(entries)}
    with (d/'build.log').open('w') as log:
        for mode, flags in MODES.items():
            ref, cand, exe = d/f'ref-{mode}.o', d/f'cand-{mode}.o', d/f'harness-{mode}'
            ok = run(cc + flags + [f'-D{fn}=reference_chunk', '-c', str(a.original/'chunks'/(name + '.c')), '-o', str(ref)], log).returncode == 0
            ok = ok and run(cc + flags + ['-I', str(a.candidate.resolve()), f'-D{fn}=candidate_chunk', '-c', str(a.candidate/'chunks'/(name + '.c')), '-o', str(cand)], log).returncode == 0
            ok = ok and run(cc + flags + ['-I', str(HERE), str(HERE/'harness.c'), str(d/'entries.c')] + libs[mode] + [str(ref), str(cand), '-o', str(exe)], log).returncode == 0
            if not ok:
                result[mode] = 'BUILD FAILED'; continue
            r = subprocess.run([str(exe), str(a.trials)], text=True, capture_output=True)
            result[mode] = (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else f'exit {r.returncode}'
    return name, result

results = {}
with cf.ThreadPoolExecutor(a.jobs) as pool:
    for name, res in pool.map(check, chosen):
        results[name] = res
        print(name, res['entries'], res.get('o2'), '|', res.get('san'), flush=True)
(out/'report.json').write_text(json.dumps(results, indent=1) + '\n')
bad = [n for n, r in results.items() if not (str(r.get('o2')).startswith('PASS') and str(r.get('san')).startswith('PASS'))]
print('ALL PASS' if not bad else f'FAILURES: {bad}')
