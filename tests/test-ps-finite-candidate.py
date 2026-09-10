"""Compare actual isolated candidate helper bodies with pinned reference code."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
candidate = Path(sys.argv[1]).read_text()
probe = (root / "tests/probe-ps-finite.c").read_text()
bodies = []
for operation in ("add", "sub"):
    name = f"ppc_ps_{operation}_op"
    body = candidate.split(f"void {name}(", 1)[1].split("\n}", 1)[0]
    bodies.append(f"static void candidate_{operation}(" + body + "\n}\n")
replacement = "\n".join(bodies) + """
static void candidate(CPUState* cpu, u8 d, u8 a, u8 b, bool subtract) {
    if (subtract) candidate_sub(cpu,d,a,b);
    else candidate_add(cpu,d,a,b);
}
"""
start = probe.index("static void candidate(")
end = probe.index("\nstatic u64 random_bits", start)
probe = probe[:start] + replacement + probe[end:]
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "candidate.c"
    binary = Path(directory) / "candidate"
    source.write_text(probe)
    subprocess.run(["clang", "-O2", "-std=c11", "-ffp-contract=off", "-fno-fast-math",
                    "-ffunction-sections", "-fdata-sections",
                    "-I", str(root / "ref/ModernGekko/vendor/dolphin/GXRuntime/src/core"),
                    "-I", str(root / "ref/ModernGekko/vendor/dolphin/GXRuntime/include"),
                    str(source), "-Wl,-dead_strip", "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
