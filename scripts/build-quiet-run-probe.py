"""Compile private full Run objects with the cached Simulator core flags.

No cached object, reference source, app, module selection, or save is changed.
Retain disassembly and exact commands before deciding on a cost experiment.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
build = root / 'generated/build/ios-simulator-core'
source = root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
entries = json.loads((build / 'compile_commands.json').read_text())
entries = [entry for entry in entries if entry['file'] == str(source)]
assert len(entries) == 1
entry = entries[0]
command = shlex.split(entry['command'])
assert '-O3' in command and '-DNDEBUG' in command
assert '-mios-simulator-version-min=16.0' in command
assert '-fno-strict-aliasing' in command and '-fno-exceptions' in command
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
original = source.read_text()
start = original.index('        do\n        {\n          if (dispatch_trace')
end = original.index('\n        SyncOut();', start)
loop = original[start:end]
for old, new, count in [
    ('if (dispatch_trace &&', 'if (!Quiet && dispatch_trace &&', 1),
    ('lockstep_enabled &&', '!Quiet && lockstep_enabled &&', 1),
    ('if (m_collect_dispatch_samples &&', 'if (!Quiet && m_collect_dispatch_samples &&', 1),
    ('if (m_has_rel_modules)', 'if (!Quiet && m_has_rel_modules)', 2),
    ('if (m_direct_boundary_enabled)', 'if (!Quiet && m_direct_boundary_enabled)', 1),
]:
    assert loop.count(old) == count, old
    loop = loop.replace(old, new)
replacement = '''        const auto native_burst = [&]<bool Quiet>() {
''' + loop + '''
        };
        if (!dispatch_trace && !lockstep_enabled && !m_collect_dispatch_samples &&
            !m_has_rel_modules && !m_direct_boundary_enabled)
          native_burst.template operator()<true>();
        else
          native_burst.template operator()<false>();'''
candidate = original[:start] + replacement + original[end:]
cached_object = Path(entry['output'])
inputs = [source, cached_object, build / 'compile_commands.json']
before = {str(path): sha(path) for path in inputs}
report = {'unchanged_inputs': before, 'original_command': command, 'variants': {}}
for name, text in [('control', original), ('candidate', candidate)]:
    src = out / (name + '.cpp')
    obj = out / (name + '.o')
    src.write_text(text)
    invocation = command.copy()
    invocation[invocation.index('-c') + 1] = str(src)
    invocation[invocation.index('-o') + 1] = str(obj)
    subprocess.run(invocation, cwd=entry['directory'], check=True)
    assembly = subprocess.check_output(
        ['xcrun', 'llvm-objdump', '--disassemble', '--demangle', str(obj)], text=True)
    (out / (name + '.asm')).write_text(assembly)
    sizes = subprocess.check_output(['xcrun', 'size', '-m', str(obj)], text=True)
    (out / (name + '.size.txt')).write_text(sizes)
    report['variants'][name] = {'source_sha256': sha(src), 'object_sha256': sha(obj),
                                'command': invocation, 'sizes': sizes}
assert all(sha(Path(path)) == digest for path, digest in before.items())
report['boundary'] = 'Full actual Run objects, not linked or executed; no performance claim.'
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({name: row['sizes'] for name, row in report['variants'].items()}, indent=2))
