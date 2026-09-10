"""Build isolated control/candidate Run objects with cached real runner flags."""
from pathlib import Path
import hashlib
import json
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
build = root/'generated/build/moderngekko-desktop'
source = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
out = root/'generated/run-lookup-r467'
out.mkdir(exist_ok=False)
original = source.read_text()
start = original.index('  const auto fast_dispatchable_at = [this](u32 address) {')
end = original.index('\n  };', start) + len('\n  };')
candidate = original[:start] + (root/'patches/experiments/run-lookup-snapshot.inc').read_text().rstrip() + original[end:]
commands = subprocess.check_output(['ninja', '-t', 'commands'], cwd=build, text=True).splitlines()
command = shlex.split(next(c for c in commands if c.endswith(' -c '+str(source))))
old_object = build/command[command.index('-o')+1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p):sha(p) for p in [source, old_object,
          root/'generated/macos/GalaxyPad.app/Contents/MacOS/GalaxyPadRunner']}
report = {'unchanged_inputs':before, 'command':command, 'variants':{}}
for name, text in [('control', original), ('candidate', candidate)]:
    src = out/(name+'.cpp'); src.write_text(text)
    obj = out/(name+'.o')
    args = command.copy()
    args[args.index('-c')+1] = str(src)
    for flag, path in [('-o',obj), ('-MF',out/(name+'.d')), ('-MT',obj)]:
        args[args.index(flag)+1] = str(path)
    subprocess.run(args, cwd=build, check=True)
    assembly = subprocess.check_output(['xcrun', 'llvm-objdump',
        '--disassemble-symbols=__ZN16StaticRecompCore3RunEv', str(obj)], text=True)
    (out/(name+'.asm')).write_text(assembly)
    report['variants'][name] = {'object_sha256':sha(obj), 'source_sha256':sha(src)}
assert all(sha(Path(p)) == digest for p,digest in before.items())
report['boundary'] = 'Isolated object compilation only; not linked, installed or gameplay-tested.'
(out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
print('Both real-flag Run objects compile; source, cached object and installed runner unchanged')
