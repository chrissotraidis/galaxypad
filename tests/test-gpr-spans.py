"""Census boundaries, not a generated-code optimization test."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'scripts/audit-gpr-spans.py'
spec = importlib.util.spec_from_file_location('audit', path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def instruction(pc, body='ctx->gpr[3] = ctx->gpr[4] + 1u;', op='addi'):
    return f'label_{pc:08X}:\n    ctx->pc = 0x{pc:08X}u;\n    // {pc:08X}: {op} r3, r4, 1\n    {body}\n\n'


def scan(*instructions):
    return audit.spans('\nvoid func_80001000(CPUState* ctx) {\n' + ''.join(instructions))

assert scan(instruction(0x1000), instruction(0x1004)) == [[0x1000, 0x1004]]
assert scan(instruction(0x1000), instruction(0x1008)) == [[0x1000], [0x1008]]
for body, op in [('ctx->gpr[3] = callback(ctx);', 'addi'),
                 ('ctx->gpr[3] = ctx->fpscr;', 'addi'),
                 ('ctx->gpr[3] = 1u; return;', 'addi'),
                 ('ctx->downcount -= 4; ctx->gpr[3] = 1u;', 'addi'),
                 ('ctx->gpr[3] = 1u;', 'add.'),
                 ('ctx->gpr[3] = mem_read32(ctx, 4u);', 'lwz')]:
    assert scan(instruction(0x1000), instruction(0x1004, body, op),
                instruction(0x1008)) == [[0x1000], [0x1008]]
assert audit.spans('') == []
print('GPR census: adjacency, discontinuities, callbacks, status, cycles and exits pass')
