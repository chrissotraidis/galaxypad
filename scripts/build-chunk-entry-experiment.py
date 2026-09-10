#!/usr/bin/env python3
"""Link the tested one-chunk candidate with exact accepted unchanged objects."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--thp-kernels', action='store_true', help='Build the source-pinned two-kernel experiment instead of the historical entry split')
args = parser.parse_args()

root = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

accepted = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
expected = '494c2a71d16963cf720af228ff8b9323a1d5b2967776cb759aa11f161beb3fbe'
assert sha(accepted) == expected
generated = (accepted.parent/'dolrecomp-output').resolve()
build = generated.parent/'module-build'
assert sha(build/'gRMGE01_recomp.dylib') == expected
if args.thp_kernels:
    candidate = root/'generated/thp-kernels-r198-exits/candidate.c'
    assert sha(candidate) == '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
    original = generated/'RMGE01_generated/chunks/chunk_1102_text1_804520A0.c'
    assert sha(original) == 'f2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61'
    experiment_name = 'thp-kernels-r199'
else:
    candidate = root/'generated/chunk-entry-r182/candidate.c'
    assert sha(candidate) == 'd248002b3b8021c79cd6b2c4ea1d15f015dd0b447b31fe060d54354dd45fe32b'
    original = generated/'RMGE01_generated/chunks/chunk_1103_text1_804530A0.c'
    assert sha(original) == 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
    experiment_name = 'chunk-entry-r184'
experiment = root/'generated'/experiment_name
assert not experiment.exists(), 'Never overwrite an existing experiment'
experiment.mkdir()
output = experiment/'gRMGE01_recomp.dylib'
rows = []
for header, variables in re.findall(r'^build ([^\n]+)\n((?:  [^\n]*\n)*)', (build/'build.ninja').read_text(), re.M):
    target, inputs = header.split(': ', 1)
    rule, _, inputs = inputs.partition(' ')
    rows.append((target, rule, inputs, dict(re.findall(r'^  (\w+) = (.*)$', variables, re.M))))
matches = [r for r in rows if r[1].startswith('C_COMPILER_') and r[2].split(' || ')[0] == str(original)]
assert len(matches) == 1
target, _, _, fields = matches[0]
flags = shlex.split(fields['DEFINES']+' '+fields['INCLUDES']+' '+fields['FLAGS'])
assert [f for f in flags if re.fullmatch('-O[0-3sz]', f)][-1] == '-O2'
assert all(f in flags for f in ('-flto=thin', '-ffp-contract=off', '-fno-fast-math'))
profiles = [f.split('=', 1)[1] for f in flags if f.startswith('-fprofile-instr-use=')]
assert len(profiles) == 1 and sha(Path(profiles[0])) == 'f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
obj = experiment/'candidate.o'
compile_command = ['/usr/bin/clang', *flags, '-c', str(candidate), '-o', str(obj)]
links = [r for r in rows if r[0] == 'gRMGE01_recomp.dylib']
assert len(links) == 1
_, _, inputs, fields = links[0]
objects = shlex.split(inputs.split(' | ')[0])
assert len(objects) == 1329 and target in objects
assert sum('/chunks/chunk_' in p for p in objects) == 1322
identities = {}
for name in objects:
    path = build/name
    assert path.is_file() and path.stat().st_mtime_ns <= (build/'gRMGE01_recomp.dylib').stat().st_mtime_ns
    identities[name] = sha(path)
response = experiment/'objects.rsp'
response.write_text('\n'.join(shlex.quote(str(obj if name == target else build/name)) for name in objects)+'\n'+fields['LINK_LIBRARIES']+'\n')
assert fields['PRE_LINK'] == fields['POST_BUILD'] == ':'
link = ['/usr/bin/clang', *shlex.split(fields['LANGUAGE_COMPILE_FLAGS']+' '+fields['ARCH_FLAGS']+' '+fields['LINK_FLAGS']),
        '-o', str(output), fields['SONAME_FLAG'], fields['INSTALLNAME_DIR']+fields['SONAME'], '@'+str(response)]
(experiment/'build-provenance.json').write_text(json.dumps(dict(
    accepted_sha256=expected, candidate_sha256=sha(candidate), selected=False,
    accepted_objects_sha256=identities, commands=[compile_command, link]), indent=2)+'\n')
manifest = (accepted.parent/'manifest.txt').read_text().replace('module_sources_fnv1a=', 'reference_module_sources_fnv1a=')
(experiment/'manifest.txt').write_text(manifest+'experiment='+experiment_name+'\nselected=false\nsource_overlay=build-provenance.json\n')
(experiment/'dolrecomp-output').symlink_to(generated, target_is_directory=True)
for command in (compile_command, link):
    print('Compile candidate' if '-c' in command else 'Link candidate, 1328 unchanged objects reused', flush=True)
    subprocess.run(command, cwd=build, check=True)
assert sha(accepted) == expected
subprocess.run([str(root/'scripts/audit-module.sh'), str(output)], check=True)
print('Unselected candidate SHA256='+sha(output), flush=True)
