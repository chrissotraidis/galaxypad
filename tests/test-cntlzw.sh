#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 - "$root" <<'PY'
import ast, json, pathlib, re, subprocess, sys, tempfile
root = pathlib.Path(sys.argv[1])
checkout = root / 'ref/ModernGekko/vendor/dolphin/DolRecomp'
# Test the retained experiment in a temporary tree, never the default generator.
emitter = subprocess.check_output(['git', '-C', str(checkout), 'show',
    json.loads((root/'config/dependencies.lock.json').read_text())['repositories']['dolRecomp']['upstreamRevision'] + ':src/backend/emitter.c'], text=True)
with tempfile.TemporaryDirectory(prefix='galaxypad-cntlzw-emitter-') as temporary:
    candidate = pathlib.Path(temporary) / 'src/backend/emitter.c'
    candidate.parent.mkdir(parents=True)
    candidate.write_text(emitter)
    subprocess.run(['git', 'apply', str(root / 'patches/experiments/cntlzw-intrinsic.patch')],
                   cwd=temporary, check=True)
    emitter = candidate.read_text()
case = emitter.split('case PPC_OP_CNTLZW:', 1)[1].split('break;', 1)[0]
assert 'emit_record_if_needed(out, inst, inst->rA);' in case
lines = []
for literal, operand in re.findall(r'fprintf\(out, ("(?:[^"\\]|\\.)*")(?:, (inst->r[SA]))?\);', case):
    text = ast.literal_eval(literal)
    if operand:
        text = text.replace('%u', '3' if operand == 'inst->rS' else '4')
    lines.append(text)
body = ''.join(lines)
assert '__builtin_clz(v)' in body and 'v ?' in body
prefix = '#include <stdint.h>\n#include <assert.h>\ntypedef uint32_t u32;\ntypedef struct { u32 gpr[32]; } CPU;\n'
source = prefix + '__attribute__((noinline)) void fast(CPU* ctx)' + body
# Compile the emitted portable branch too, without modifying compiler built-ins.
portable = body.replace('#if defined(__GNUC__) || defined(__clang__)', '#if 0')
source += '\nvoid portable(CPU* ctx)' + portable
source += r'''
u32 reference(u32 value) {
  u32 count = 32;
  while (value) { --count; value >>= 1; }
  return count;
}
void check(u32 value) {
  CPU a = {{0}}, b = {{0}};
  a.gpr[3] = b.gpr[3] = value;
  fast(&a); portable(&b);
  assert(a.gpr[4] == reference(value));
  assert(b.gpr[4] == a.gpr[4] && a.gpr[3] == value);
}
int main(void) {
  check(0); check(UINT32_MAX);
  for (unsigned i = 0; i < 32; ++i) {
    check(1u << i); check((1u << i) - 1); check(~(1u << i));
  }
  u32 x = 0x12345678;
  for (unsigned i = 0; i < 1000000; ++i) {
    x ^= x << 13; x ^= x >> 17; x ^= x << 5; check(x);
  }
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-cntlzw-') as temporary:
    base = pathlib.Path(temporary)
    c = base / 'test.c'
    c.write_text(source)
    subprocess.run(['clang', '-O2', '-fsanitize=undefined', str(c), '-o', str(base/'test')], check=True)
    subprocess.run([str(base/'test')], check=True)
    subprocess.run(['clang', '-O2', '-S', str(c), '-o', str(base/'test.s')], check=True)
    if subprocess.check_output(['uname', '-m'], text=True).strip() == 'arm64':
        assembly = (base/'test.s').read_text().split('_fast:', 1)[1].split('.cfi_endproc', 1)[0]
        assert re.search(r'\bclz\s+w', assembly), assembly
print('CNTLZW emitted intrinsic/portable differential and ARM64 lowering tests passed')
PY
