#!/usr/bin/env python3
"""Prepare an unselected optional preserve_none host/module boundary.

Use with create-preserve-none-experiment.py's generated tree. This copies source
into a new directory, writes an unapplied patch and a Clang VFS overlay, and does
not change the canonical runtime, build anything, or select a module.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'ref/ModernGekko/vendor/dolphin'
RUN_PATH = Path('Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp')
MODULE_PATH = Path('module-template/module_export.c')
SYMBOL = 'galaxypad_dispatch_preserve_none_v1'


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Source anchor missing or ambiguous: ' + old)
    return text.replace(old, new)


def create(output):
    output = output.resolve()
    if output.exists() or RUNTIME == output or RUNTIME in output.parents:
        raise ValueError('Output must be a new directory outside the runtime tree')
    original_run = (RUNTIME / RUN_PATH).read_text()
    original_module = (RUNTIME / MODULE_PATH).read_text()
    if SYMBOL in original_run or SYMBOL in original_module:
        raise ValueError('Input already has the experimental symbol')
    run = replace_once(original_run, 'void StaticRecompCore::Run()\n{\n', '''void StaticRecompCore::Run()
{
  typedef __attribute__((preserve_none)) int (*PreserveNoneDispatchV1)(CPUState*, u32);
  const PreserveNoneDispatchV1 preserve_none_dispatch = m_module && m_library.IsOpen() ?
      reinterpret_cast<PreserveNoneDispatchV1>(
          m_library.GetSymbolAddress("galaxypad_dispatch_preserve_none_v1")) : nullptr;
''')
    run = replace_once(run, '          m_module->dispatch(&m_guest, linked_dispatch_address);', '''          if (preserve_none_dispatch)
            preserve_none_dispatch(&m_guest, linked_dispatch_address);
          else
            m_module->dispatch(&m_guest, linked_dispatch_address);''')
    # flatten prevents an outlined normal-ABI dolrecomp_call helper from putting
    # the callee-saved spill/restore work back on this optional dispatch path.
    module = original_module + '''
// Optional experiment symbol. The original module descriptor ABI remains usable.
RECOMP_MODULE_EXPORT __attribute__((preserve_none,flatten)) int
    galaxypad_dispatch_preserve_none_v1(CPUState* ctx, u32 address)
{
    return dolrecomp_call(ctx, address);
}
'''
    changes = [(RUN_PATH, original_run, run), (MODULE_PATH, original_module, module)]
    output.mkdir(parents=True)
    shutil.copytree(RUNTIME / 'module-template', output / 'module-template')
    provenance = {'selected': False, 'runtime': str(RUNTIME), 'files': {}}
    patch = []
    for relative, original, candidate in changes:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(candidate)
        patch.extend(difflib.unified_diff(original.splitlines(keepends=True),
                     candidate.splitlines(keepends=True),
                     fromfile='a/' + str(relative), tofile='b/' + str(relative)))
        provenance['files'][str(relative)] = {
            'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
            'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest()}
    (output / 'boundary.patch').write_text(''.join(patch))
    # A separate core build can use -ivfsoverlay=<this file> to compile the
    # candidate Run without changing any canonical source file.
    overlay = {'version': 0, 'roots': [{'type': 'file',
        'name': str(RUNTIME / RUN_PATH), 'external-contents': str(output / RUN_PATH)}]}
    (output / 'host-overlay.json').write_text(json.dumps(overlay, indent=2) + '\n')
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(f'Prepared optional boundary at {create(args.output)}; selected=false')
