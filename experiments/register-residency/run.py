#!/usr/bin/env python3
"""Reproduce the register-residency screen against private generated chunks.

Reads two SHA-pinned generated chunks and the pinned GXRuntime headers, writes
only to a new output directory, and never builds a module, app or runtime.
"""
from pathlib import Path
import argparse, hashlib, json, re, statistics, subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHUNKS = {
    'chunk_1299_text1_805170A0': ('func_805170A0', '9b221ad3e1b417287e425640cc318e30fc5a6378e2956bf65a929be455acfd94'),
    'chunk_1202_text1_804B60A0': ('func_804B60A0', '38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'),
}
RUNTIME_SOURCES = ['cpu.c', 'cpu_exception.c', 'cpu_interpreter.c', 'cpu_interpreter_float.c',
                   'cpu_interpreter_integer.c', 'cpu_interpreter_table.c']
SANITIZE = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=undefined']

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--generated', type=Path, default=ROOT/'generated/aot/device-fresh/RMGE01_generated')
p.add_argument('--runtime', type=Path, default=ROOT/'ref/ModernGekko/vendor/dolphin',
               help='Pinned RecompCore checkout (clean, at the dependency lock revision)')
p.add_argument('--output', type=Path, required=True)
args = p.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
gen, rt = args.generated.resolve(), args.runtime.resolve()


def sh(cmd):
    r = subprocess.run(cmd, cwd=out, text=True, capture_output=True)
    with (out/'commands.log').open('a') as log:
        log.write(' '.join(map(str, cmd)) + '\n' + r.stdout + r.stderr + '\n')
    if r.returncode:
        raise SystemExit(f'failed: {cmd[0]} ... (see commands.log)')
    return r.stdout + r.stderr


sources = {}
for name, (_, digest) in CHUNKS.items():
    text = (gen/'chunks'/(name + '.c')).read_text()
    actual = hashlib.sha256(text.encode()).hexdigest()
    if actual != digest:
        raise SystemExit(f'{name} differs from the screened source: {actual}')
    sources[name] = text
git = lambda *a: subprocess.run(['git', '-C', str(rt), *a], text=True, capture_output=True).stdout.strip()
report = {'runtime_revision': git('rev-parse', 'HEAD'),
          'runtime_gxruntime_dirty': bool(git('status', '--porcelain', '--', 'GXRuntime')),
          'chunks': {k: v[1] for k, v in CHUNKS.items()},
          'differential': {}, 'static_iphoneos_o2': {}, 'loop_cycles': {}}

(out/'RMGE01.h').symlink_to(gen/'RMGE01.h')
(out/'gp_memmap.h').write_text((HERE/'gp_memmap.h').read_text())
for d in ('snapshot', 'region', 'o2', 'san'):
    (out/d).mkdir()


def with_header(s):
    return s.replace('#include "../RMGE01.h"', '#include "../RMGE01.h"\n#include "../gp_memmap.h"', 1)


for name, text in sources.items():
    s = with_header(text)
    s = re.sub(r'^((?:static )?void (?:func|loop)_[0-9A-F]+\(CPUState\* ctx\) \{)$',
               r'\1\n    GP_MM_DECL(ctx);', s, flags=re.M)
    s = re.sub(r'\bmem_(read|write)(8|16|32|64)\(ctx, ', r'gp_mm_\1\2(&gp_mm, ctx, ', s)
    (out/'snapshot'/(name + '.c')).write_text(s)
    body = text[text.index(f'void {CHUNKS[name][0]}(CPUState* ctx) {{'):]
    entries = re.findall(r'case (0x[0-9A-F]+)u:', body[body.index('switch (ctx->pc) {'):body.index('default:')])
    (out/f'entries_{name}.c').write_text('const unsigned gp_entries[]={%s};\nconst unsigned gp_entry_count=%d;\n'
                                         % (','.join(entries), len(entries)))
loop_name = 'chunk_1299_text1_805170A0'
s = with_header(sources[loop_name])
a = s.index('static void loop_80517F10(CPUState* ctx) {')
b = s.index('\n}\n', a) + 3
(out/'region'/(loop_name + '.c')).write_text(s[:a] + (HERE/'region_80517F10.c').read_text() + s[b:])

inc = ['-I', str(gen), '-I', str(rt/'GXRuntime/include'), '-I', str(rt/'Source/Core/Core/PowerPC/StaticRecomp')]
common = ['xcrun', 'clang', '-std=gnu11', '-ffp-contract=off', '-fno-fast-math', '-w'] + inc
rtsrc = [str(rt/'GXRuntime/src/core'/f) for f in RUNTIME_SOURCES]


def objects(tag, flags, name, variant):
    fn = CHUNKS[name][0]
    ref, cand = out/tag/f'{name}.ref.o', out/tag/f'{name}.{variant}.o'
    if not ref.exists():
        sh(common + flags + [f'-D{fn}=reference_chunk', '-c', str(gen/'chunks'/(name + '.c')), '-o', str(ref)])
    sh(common + flags + [f'-D{fn}=candidate_chunk', '-c', str(out/variant/(name + '.c')), '-o', str(cand)])
    return ref, cand


for tag, flags in (('o2', ['-O2']), ('san', SANITIZE)):
    for name, variant in [(n, 'snapshot') for n in CHUNKS] + [(loop_name, 'region')]:
        ref, cand = objects(tag, flags, name, variant)
        exe = out/tag/f'harness-{name}-{variant}'
        sh(common + flags + ['-I', str(HERE), str(HERE/'harness.c'), str(out/f'entries_{name}.c')]
           + rtsrc + [str(ref), str(cand), '-o', str(exe)])
        report['differential'][f'{tag}/{name}/{variant}'] = sh([str(exe), '2']).strip()
    exe = out/tag/'loopcheck'
    sh(common + flags + ['-I', str(HERE), str(HERE/'loopcheck.c'), str(out/f'entries_{loop_name}.c')] + rtsrc
       + [str(out/tag/f'{loop_name}.ref.o'), str(out/tag/f'{loop_name}.region.o'), '-o', str(exe)])
    report['differential'][f'{tag}/loop_80517F10/targeted'] = sh([str(exe)]).strip()

ios = ['xcrun', '-sdk', 'iphoneos', 'clang', '-arch', 'arm64', '-miphoneos-version-min=16.0', '-std=gnu11', '-O2',
       '-ffp-contract=off', '-fno-fast-math', '-fPIC', '-fvisibility=hidden', '-DNDEBUG', '-w', '-S'] + inc


def count(asm):
    lines = asm.read_text().splitlines()
    ins = [l.split()[0] for l in lines if l.startswith('\t') and l[1:2].isalpha()]
    return {'instructions': len(ins), 'loads': sum(i.startswith('ld') for i in ins),
            'stores': sum(i.startswith('st') for i in ins), 'stack_refs': sum('[sp' in l for l in lines)}


for name in CHUNKS:
    for label, src in (('reference', gen/'chunks'/(name + '.c')), ('snapshot', out/'snapshot'/(name + '.c'))):
        asm = out/f'{name}.{label}.s'
        sh(ios + [str(src), '-o', str(asm)])
        report['static_iphoneos_o2'][f'{name}/{label}'] = count(asm)

bench = out/'o2'/'loopbench'
sh(common + ['-O2', str(HERE/'loopbench.c')] + rtsrc
   + [str(out/'o2'/f'{loop_name}.ref.o'), str(out/'o2'/f'{loop_name}.region.o'), '-o', str(bench)])


def counters(variant, calls):
    r = subprocess.run(['/usr/bin/time', '-l', str(bench), variant, str(calls)], text=True, capture_output=True, check=True)
    get = lambda key: int(re.search(r'(\d+)\s+' + key, r.stderr).group(1))
    return int(re.search(r'iterations=(\d+)', r.stdout).group(1)), get('instructions retired'), get('cycles elapsed')


for variant, label in (('r', 'reference'), ('c', 'region')):
    rows = []
    for _ in range(5):
        i1, n1, c1 = counters(variant, 20)
        i2, n2, c2 = counters(variant, 60)
        rows.append(((n2 - n1) / (i2 - i1), (c2 - c1) / (i2 - i1)))
    report['loop_cycles'][label] = {'instructions_per_iteration': statistics.median(r[0] for r in rows),
                                    'cycles_per_iteration': statistics.median(r[1] for r in rows), 'samples': rows}
(out/'report.json').write_text(json.dumps(report, indent=1) + '\n')
print(json.dumps({k: report[k] for k in ('differential', 'static_iphoneos_o2')}, indent=1))
print(json.dumps({k: {m: round(v[m], 2) for m in ('instructions_per_iteration', 'cycles_per_iteration')}
                  for k, v in report['loop_cycles'].items()}, indent=1))
