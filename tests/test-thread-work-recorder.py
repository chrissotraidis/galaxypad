"""Private header overlay, fake-provider lifetime tests and release exclusion."""
import importlib.util
import csv
import errno
import os
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
environment=dict(os.environ)
environment.pop('GALAXYPAD_THREAD_WORK_TIMING',None)
spec=importlib.util.spec_from_file_location('overlay',root/'scripts/prepare-thread-work-recorder.py')
overlay=importlib.util.module_from_spec(spec); spec.loader.exec_module(overlay)
with tempfile.TemporaryDirectory(prefix='galaxypad-thread-work-') as temporary:
    folder=Path(temporary)
    subprocess.run(['clang++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                    '-fsanitize=address,undefined','-pthread',
                    str(root/'tests/thread-work-recorder.cpp'),'-o',str(folder/'test')],check=True)
    subprocess.run([str(folder/'test'),str(folder)],check=True)
    overlay.prepare(folder/'include')
    try:
        overlay.prepare(folder/'include')
    except FileExistsError:
        pass
    else:
        raise AssertionError('Overlay overwrote existing output')
    source=(root/'patches/experiments/vi-timing-recorder.h').read_text()
    for bad in (0,16385,1000000000):
        try:
            overlay.transform(source,bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Unbounded private capacity accepted')
    overlay.prepare(folder/'large',65536)
    large_fixture=(root/'tests/thread-work-vi.cpp').read_text().replace(
        '    recorder.Record();', '    for (unsigned sample=0;sample<10000;++sample) recorder.Record();')
    (folder/'large.cpp').write_text(large_fixture)
    subprocess.run(['clang++','-std=c++17','-O2','-pthread','-DGALAXYPAD_PRIVATE_THREAD_WORK=1',
                    '-I'+str(folder/'large'),str(folder/'large.cpp'),'-o',str(folder/'large-test')],check=True)
    large_output=folder/'large-output'; large_output.mkdir()
    subprocess.run([str(folder/'large-test'),str(large_output)],check=True,env=environment)
    with (large_output/'vi.csv').open() as stream:
        assert stream.readline().strip()=='# dropped=0'
        large_vi=list(csv.DictReader(stream))
    with (large_output/'vi.csv.work').open() as stream:
        assert stream.readline().startswith('# dropped=0 ')
        large_work=list(csv.DictReader(stream))
    assert len(large_vi)==20000
    assert {r['wall_ns'] for r in large_vi}=={r['vi_ns'] for r in large_work}
    try:
        overlay.transform(source.replace('    const auto sample = clock();',''))
    except ValueError:
        pass
    else:
        raise AssertionError('Missing source anchor accepted')
    # Mechanical include substitution: exercise existing export/lifetime tests.
    fixture=(root/'tests/vi-timing-recorder.cpp').read_text().replace(
        '../patches/experiments/vi-timing-recorder.h','vi-timing-recorder.h')
    (folder/'fixture.cpp').write_text(fixture)
    for private in (False,True):
        output=folder/('private' if private else 'ordinary'); output.mkdir()
        command=['clang++','-std=c++17','-O2','-pthread','-I',str(folder/'include')]
        if private:
            command += ['-DGALAXYPAD_PRIVATE_THREAD_WORK=1']
        subprocess.run(command+[str(folder/'fixture.cpp'),'-o',str(output/'test')],check=True)
        subprocess.run([str(output/'test'),str(output)],check=True,env=environment)
        strings=subprocess.check_output(['strings',str(output/'test')])
        assert (b'thread_selfcounts' in strings) == private
        subprocess.run(command+[str(root/'tests/thread-work-vi.cpp'),'-o',str(output/'live')],check=True)
        subprocess.run([str(output/'live'),str(output)],check=True,env=environment)
        sidecar=output/'vi.csv.work'
        assert sidecar.exists() == private
        if private:
            with (output/'vi.csv').open() as stream:
                vi=list(csv.DictReader(line for line in stream if not line.startswith('#')))
            with sidecar.open() as stream:
                work=list(csv.DictReader(line for line in stream if not line.startswith('#')))
            assert len(vi)==2 and len(work)>=2
            assert {row['vi_ns'] for row in work} == {row['wall_ns'] for row in vi}
            errors={int(row['error']) for row in work}
            assert errors <= {0, errno.ENOTSUP, errno.ENOSYS}, work
            assert all(int(row['before_ns'])<=int(row['after_ns']) for row in work)
            if errors == {0}:
                assert sum(int(row['instructions']) for row in work)>0
                assert sum(int(row['cycles']) for row in work)>0
                print('Live thread PMU counts are available on this host.')
            else:
                print(f'Live thread PMU coverage unavailable: errors={sorted(errors)} samples={work}; deterministic provider coverage passed.')
print('Private recorder failure/reset/drop/disabled tests pass; VI overlay lifetime passes both modes; ordinary binary excludes SPI symbol')
