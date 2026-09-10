"""Link private same-graph runners differing only in the R467 Run object."""
from pathlib import Path
import hashlib
import json
import shlex
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
build = root/'generated/build/moderngekko-desktop'
objects = root/'generated/run-lookup-r467'
out = root/'generated/run-lookup-r468'
out.mkdir(exist_ok=False)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = json.loads((objects/'report.json').read_text())
assert all(sha(Path(p)) == digest for p,digest in report['unchanged_inputs'].items())
commands = subprocess.check_output(['ninja', '-t', 'commands', 'moderngekko-run'], cwd=build, text=True).splitlines()
line = next(line for line in commands if ' -o moderngekko-run ' in line)
link = shlex.split(next(part for part in line.split(' && ') if ' -o moderngekko-run ' in part))
core = next(p for p in link if p.endswith('/libcore.a'))
member = 'StaticRecompCore_Run.cpp.o'
assert subprocess.check_output(['xcrun','ar','-t',str(build/core)],text=True).splitlines().count(member) == 1
inputs = [Path(p) if Path(p).is_absolute() else build/p for p in link if p.endswith(('.a','.o'))]
before = {str(p):sha(p) for p in inputs}
result = {'inputs':before, 'variants':{}}
for name in ['control','candidate']:
    directory = out/name; directory.mkdir()
    obj = directory/member
    assert sha(objects/(name+'.o')) == report['variants'][name]['object_sha256']
    shutil.copy2(objects/(name+'.o'), obj)
    archive = directory/'libcore.a'
    shutil.copy2(build/core, archive)
    subprocess.run(['xcrun','ar','r',str(archive),str(obj)],check=True)
    subprocess.run(['xcrun','ranlib',str(archive)],check=True)
    runner = directory/'GalaxyPadRunner'
    args = [str(archive) if p == core else p for p in link]
    args[args.index('-o')+1] = str(runner)
    subprocess.run(args,cwd=build,check=True)
    subprocess.run(['codesign','--force','--sign','-',str(runner)],check=True)
    result['variants'][name] = {'runner_sha256':sha(runner),'object_sha256':sha(obj),'link':args}
assert all(sha(Path(p)) == digest for p,digest in before.items())
result['boundary'] = 'Same cached link graph; only Run object differs. Private runners, not installed or accepted.'
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({name:row['runner_sha256'] for name,row in result['variants'].items()},indent=2))
