"""Map retained frontend instrumentation onto one current generated chunk.

Builds only a temporary coverage object. Never executes or selects a module.
Rejects counter/hash diagnostics; records the expected newer-object timestamp
warning because this coverage object is freshly compiled from retained source.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shlex
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--chunk', default='804B60A0',
                    help='Eight-digit hexadecimal generated chunk entry')
parser.add_argument('--generated-dir', type=Path,
                    help='Current generated source directory (otherwise retained R387)')
parser.add_argument('--build-dir', type=Path, help='Matching module build directory')
parser.add_argument('--profile', type=Path, help='Matching indexed instrumentation profile')
args = parser.parse_args()
if not re.fullmatch('[0-9A-Fa-f]{8}', args.chunk):
    parser.error('Chunk must be an eight-digit hexadecimal address')
address = args.chunk.upper()
function_name = 'func_' + address
if args.generated_dir:
    matches = list(args.generated_dir.resolve().glob('chunks/*' + address + '.c'))
    if not args.build_dir:
        parser.error('--generated-dir requires --build-dir')
else:
    matches = list((root/'generated/modules-scale-r387/RMGE01').glob(
        '*/dolrecomp-output/RMGE01_generated/chunks/*' + address + '.c'))
assert len(matches) == 1
chunk = matches[0]
build = args.build_dir.resolve() if args.build_dir else chunk.parents[3]/'module-build'
ninja = (build/'build.ninja').read_text()
stanzas = [s for s in ninja.split('\nbuild ') if re.match(r'[^\n]*'+re.escape(chunk.name)+r'\.o:', s)]
assert len(stanzas) == 1
flags = []
for key in ['DEFINES', 'FLAGS', 'INCLUDES']:
    found = re.search(r'^  '+key+r' = (.*)$', stanzas[0], re.M)
    assert found
    flags += shlex.split(found[1])
flags = [f for f in flags if not f.startswith(('-fprofile-instr-use=', '-flto'))]
profile = args.profile.resolve() if args.profile else root/'generated/pgo/rmge01.profdata'
with tempfile.TemporaryDirectory(prefix='galaxypad-chunk-coverage-') as directory:
    obj = Path(directory)/'chunk.o'
    subprocess.run(['xcrun', 'clang', *flags, '-fprofile-instr-generate',
                    '-fcoverage-mapping', '-c', str(chunk), '-o', str(obj)], check=True)
    result = subprocess.run(['xcrun', 'llvm-cov', 'export', str(obj),
                             '-instr-profile='+str(profile), '-name='+function_name],
                            check=True, capture_output=True, text=True)
    diagnostics = result.stderr.strip().splitlines()
    expected = f'warning: {obj}: profile data may be out of date - object is newer'
    if any(line != expected for line in diagnostics):
        raise RuntimeError('Coverage diagnostics: '+result.stderr)
    data = json.loads(result.stdout)
    functions = [f for row in data['data'] for f in row['functions'] if f['name']==function_name]
    assert len(functions) == 1
    f = functions[0]
    source = chunk.read_text().splitlines()
    function_start = source.index('void ' + function_name + '(CPUState* ctx) {')
    coverage_files = [item for row in data['data'] for item in row['files']
                      if Path(item['filename']) == chunk]
    assert len(coverage_files) == 1
    segments = coverage_files[0]['segments']
    selected, instructions = [], []
    for i, line in enumerate(source):
        if i <= function_start:
            continue  # Outlined helpers have separate counters and duplicate labels.
        if re.fullmatch(r'label_[0-9A-F]{8}:', line):
            # Some entries omit dead PC assignments and begin with a comment.
            # Query the first statement, never a comment/gap or another label.
            statement = i + 1
            while statement < len(source) and (not source[statement].strip() or
                    source[statement].lstrip().startswith('//') or
                    source[statement].strip() == '{'):
                statement += 1
            assert statement < len(source) and not source[statement].startswith('label_')
            point = (statement+1, len(source[statement])-len(source[statement].lstrip())+1)
            earlier = [s for s in segments if tuple(s[:2]) <= point]
            assert earlier
            segment = earlier[-1]
            count = segment[2] if segment[3] and not segment[5] else None
            item = dict(label=line, line=point[0], count=count, segment=segment)
            instructions.append(item)
            if line in ['label_804B6278:', 'label_804B66A0:', 'label_804B66A4:',
                        'label_804B66A8:', 'label_804B66AC:']:
                assert count is not None
                selected.append(item)
    print(json.dumps(dict(chunk_sha256=hashlib.sha256(chunk.read_bytes()).hexdigest(),
                         profile_sha256=hashlib.sha256(profile.read_bytes()).hexdigest(),
                         function_count=f['count'], function_name=function_name,
                         filenames=f['filenames'],
                         diagnostics=diagnostics,
                         selected_entries=selected,
                         instruction_entries=instructions,
                         regions=f['regions'],
                         labels={str(i+1): line for i,line in enumerate(source) if line.startswith('label_')},
                         caveat='Retained training execution counts, not current scene CPU costs.'), indent=2))
