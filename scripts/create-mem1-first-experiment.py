#!/usr/bin/env python3
"""Prepare an unselected MEM1-first resolver with original MEM2 precedence.

Only get_ram_ptr changes. The candidate reads current mapping fields at every
access, retains unsigned bounds arithmetic, and introduces no state/cache/ABI.
No source, build, selected module or app is modified by this preparation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ref/ModernGekko/vendor/dolphin/GXRuntime'
HEADER = Path('include/core/cpu.h')
BEGIN = 'static GXRUNTIME_ALWAYS_INLINE u8* get_ram_ptr('
END = '\nstatic GXRUNTIME_ALWAYS_INLINE void clear_matching_reservation('
CANDIDATE = '''static GXRUNTIME_ALWAYS_INLINE u8* get_ram_ptr(CPUState* cpu, u32 addr, u32 size, u32* out_offset) {
    u32 masked_addr = addr & ~0x40000000u;
    u32 ram_offset = masked_addr - 0x80000000u;
    u32 exram_offset = masked_addr - 0x90000000u;

    if (ram_offset <= cpu->ram_size - size) {
        // Preserve MEM2 precedence for overlapping/unusual declared windows.
        // On ordinary MEM1 hits the offset test excludes MEM2 before its
        // pointer is loaded. No mapping field is cached across callbacks.
        if (exram_offset > cpu->exram_size - size || !cpu->exram) {
            if (out_offset) *out_offset = ram_offset;
            return cpu->ram + ram_offset;
        }
    } else if (exram_offset > cpu->exram_size - size || !cpu->exram) {
        return NULL;
    }

    if (out_offset) *out_offset = (u32)-1;
    return cpu->exram + exram_offset;
}
'''


def body(text):
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError('Unknown resolver header shape')
    start = text.index(BEGIN)
    end = text.index(END, start)
    return text[start:end]


def create(output):
    output = output.resolve()
    if output.exists() or output == SOURCE or SOURCE in output.parents:
        raise ValueError('Output must be a new directory outside canonical GXRuntime')
    original = (SOURCE / HEADER).read_text()
    old = body(original)
    if 'Check MEM2 (EXRAM) first' not in old:
        raise ValueError('Input is not the original MEM2-first resolver')
    candidate = original.replace(old, CANDIDATE)
    shutil.copytree(SOURCE, output)
    (output / HEADER).write_text(candidate)
    manifest = {'selected': False, 'source': str(SOURCE), 'output': str(output),
        'change': 'get_ram_ptr ordering only; retains MEM2 precedence and live-field reads',
        'source_header_sha256': hashlib.sha256(original.encode()).hexdigest(),
        'candidate_header_sha256': hashlib.sha256(candidate.encode()).hexdigest()}
    (output / 'mem1-first-provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create(args.output), indent=2))
