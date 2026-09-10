"""Compile/link only the staged frontend, preserving the normal build products."""
from pathlib import Path
import hashlib
import json
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
build = root/'generated/build/moderngekko-desktop'
stage = root/'generated/frontend-progress-r454'
report = json.loads((stage/'report.json').read_text())
source = root/'ref/ModernGekko/tools/moderngekko_launcher.cpp'
assert hashlib.sha256(source.read_bytes()).hexdigest() == report['source_sha256']
obj = build/'CMakeFiles/moderngekko-launcher.dir/tools/moderngekko_launcher.cpp.o'
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (obj, build/'ModernGekko')}
compile_args = [arg for arg in report['command'] if arg != '-fsyntax-only']
subprocess.run(compile_args, cwd=build, check=True)
line = subprocess.check_output(['ninja', '-t', 'commands', 'moderngekko-launcher'], cwd=build, text=True).splitlines()[-1]
assert line.startswith(': && ') and line.endswith(' && :')
args = shlex.split(line[5:-5])
old = 'CMakeFiles/moderngekko-launcher.dir/tools/moderngekko_launcher.cpp.o'
assert args.count(old) == 1
args[args.index(old)] = str(stage/'frontend.o')
args[args.index('-o')+1] = str(stage/'GalaxyPadFrontend')
subprocess.run(args, cwd=build, check=True)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p,digest in before.items())
subprocess.run(['codesign', '--force', '--sign', '-', str(stage/'GalaxyPadFrontend')], check=True)
print('Isolated frontend linked; normal object/executable unchanged')
