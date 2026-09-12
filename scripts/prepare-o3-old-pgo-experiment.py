#!/usr/bin/env python3
"""Stage an isolated O3 + validated old-PGO module; execute only with --execute.

This changes the final per-TU -O2 to -O3. The original ThinLTO link already
uses -O3 and remains identical, including the old profile and strict FP flags.
It never installs, selects, or copies the candidate into an application.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'generated/build/ios-simulator-pgo-use-20260912'
PROFILE = ROOT / 'generated/runtime/ipad-iteration-1/pgo-profile-route-20260912/current-input.profdata'
BASELINE_SHA = '90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f'
PROFILE_SHA = '784f47e4904a36319b7805cd7807091d1d486ccc4cacc09f4785636d3949ca54'
MODULE = 'gRMGE01_recomp.dylib'
CONTROL_BUILD_LOG = ROOT / 'generated/runtime/ipad-iteration-1/pgo-profile-route-20260912/pgo-use-build.log'
CONTROL_BUILD_LOG_SHA = '6931729182d537eca2c216700f8a0a7d70a145bf4e16122a3f3783b104271baa'
KNOWN_PROFILE_WARNING = 'warning: no profile data available for file "cpu_interpreter_integer.c" [-Wprofile-instr-unprofiled]'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def link_command(build):
    line = subprocess.check_output(
        ['ninja', '-C', str(build), '-t', 'commands', MODULE], text=True).splitlines()[-1]
    argv = shlex.split(line)
    require(argv[:2] == [':', '&&'] and argv[-2:] == ['&&', ':'],
            'Unexpected Ninja link-command wrapper')
    require('&&' not in argv[2:-2], 'Unexpected shell operator')
    return argv[2:-2]


def validate_pins():
    require(sha(CONTROL / MODULE) == BASELINE_SHA, 'Control module hash changed')
    require(sha(PROFILE) == PROFILE_SHA, 'Validated old profile hash changed')


def logged(argv, path):
    with path.open('w') as log:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1)
        for line in proc.stdout:
            log.write(line)
            log.flush()
            print(line, end='', flush=True)
        result = proc.wait()
    require(result == 0, f'Command failed with exit {result}; see {path}')
    return path.read_text()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', help='Configure and compile after timing release')
    parser.add_argument('--validate-only', action='store_true', help='Validate an existing build; never configure or compile')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    require(1 <= args.jobs <= 16, 'jobs must be 1..16')
    require(not (args.execute and args.validate_only), 'Choose execute or validate-only')
    output = args.output.resolve()
    require(ROOT / 'generated/build' in output.parents, 'Output must be an isolated generated/build directory')
    require(output != CONTROL, 'Cannot overwrite control')
    validate_pins()
    manifest_path = output / 'experiment.json'
    if not args.execute and not args.validate_only:
        require(not output.exists(), 'Output exists; preserve prior experiment evidence')
        rows = json.loads((CONTROL / 'compile_commands.json').read_text())
        require(len(rows) == 1329, 'Unexpected control translation-unit count')
        profile_flag = '-fprofile-instr-use=' + str(PROFILE)
        for row in rows:
            argv = shlex.split(row['command'])
            require(argv.count('-O2') == 1 and profile_flag in argv and '-flto=thin' in argv,
                    'Unexpected control compile policy: ' + row['file'])
            require('-ffp-contract=off' in argv and '-fno-fast-math' in argv,
                    'Missing strict FP policy')
        link = link_command(CONTROL)
        require(profile_flag in link and '-O3' in link and '-O2' not in link,
                'Unexpected control ThinLTO link policy')
        cache = {}
        for line in (CONTROL / 'CMakeCache.txt').read_text().splitlines():
            if re.match(r'^[A-Za-z_][A-Za-z_0-9]*:[^=]+=', line):
                key, value = line.split('=', 1)
                cache[key.split(':', 1)[0]] = value
        configure = ['cmake', '-S', cache['CMAKE_HOME_DIRECTORY'], '-B', str(output), '-G', 'Ninja']
        keys = ['CMAKE_TOOLCHAIN_FILE', 'CMAKE_BUILD_TYPE', 'GAME_ID', 'GENERATED_DIR',
                'GXRUNTIME_DIR', 'CHASSIS_ABI_DIR', 'RECOMPCORE_MODULE_ENABLE_IPO',
                'CMAKE_C_FLAGS', 'CMAKE_SHARED_LINKER_FLAGS', 'CMAKE_C_FLAGS_RELEASE']
        configure += ['-D' + key + '=' + cache[key] for key in keys]
        configure += ['-DCMAKE_EXPORT_COMPILE_COMMANDS=ON', '-DRECOMPCORE_MODULE_OPT_LEVEL=3']
        inputs = {Path(row['file']) for row in rows}
        for directory in [Path(cache['GENERATED_DIR']), Path(cache['GXRUNTIME_DIR']) / 'include',
                          Path(cache['GXRUNTIME_DIR']) / 'src/core', Path(cache['CHASSIS_ABI_DIR'])]:
            inputs.update(directory.rglob('*.h'))
        inputs.update([Path(cache['CMAKE_TOOLCHAIN_FILE']),
                       Path(cache['CMAKE_HOME_DIRECTORY']) / 'CMakeLists.txt',
                       Path(cache['CMAKE_HOME_DIRECTORY']) / 'gen_module_tables.py',
                       Path(cache['GENERATED_DIR']) / 'generated_smc.txt',
                       Path(cache['GENERATED_DIR']) / 'main.dol'])
        stamps = [{'path': str(p), 'size': p.stat().st_size, 'mtime_ns': p.stat().st_mtime_ns}
                  for p in sorted(inputs)]
        output.mkdir(parents=True)
        manifest = {'status': 'prepared; no configure or build executed',
                    'control_module_sha256': BASELINE_SHA, 'profile_sha256': PROFILE_SHA,
                    'configure': configure, 'control_compile_commands': rows,
                    'control_link_command': link, 'source_stamps': stamps,
                    'module_tables_sha256': sha(CONTROL / 'module_tables.inc'),
                    'scope': 'only final per-TU O2 becomes O3; existing O3 ThinLTO link policy unchanged'}
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'Prepared {len(rows)} TUs and {len(stamps)} source/header stamps: {manifest_path}')
        print('Execute only after capture release:')
        print(shlex.join(['python3', str(Path(__file__).resolve()), '--output', str(output),
                          '--execute', '--jobs', str(args.jobs)]))
        return
    require(manifest_path.is_file(), 'Prepare this experiment first')
    manifest = json.loads(manifest_path.read_text())
    if args.validate_only:
        require((output / MODULE).is_file(), 'No existing candidate to validate')
    else:
        require(not (output / MODULE).exists(), 'Candidate module already exists; preserve evidence')
    for entry in manifest['source_stamps']:
        stat = Path(entry['path']).stat()
        require((stat.st_size, stat.st_mtime_ns) == (entry['size'], entry['mtime_ns']),
                'Source changed since staging: ' + entry['path'])
    if not args.validate_only:
        logged(manifest['configure'], output / 'configure.log')
    candidate_rows = json.loads((output / 'compile_commands.json').read_text())
    candidate = {row['file']: shlex.split(row['command']) for row in candidate_rows}
    require(len(candidate) == len(manifest['control_compile_commands']), 'Translation-unit count changed')
    for row in manifest['control_compile_commands']:
        expected = [arg.replace(str(CONTROL), str(output)) for arg in shlex.split(row['command'])]
        expected[expected.index('-O2')] = '-O3'
        require(candidate.get(row['file']) == expected,
                'Unexpected compile-command difference: ' + row['file'])
    expected_link = [arg.replace(str(CONTROL), str(output)) for arg in manifest['control_link_command']]
    require(link_command(output) == expected_link, 'Unexpected link-policy difference')
    manifest['commands_validated'] = True
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    if args.validate_only:
        log = (output / 'build.log').read_text()
        require('Linking C shared library ' + MODULE in log, 'Build log lacks completed link step')
    else:
        log = logged(['cmake', '--build', str(output), '--parallel', str(args.jobs)], output / 'build.log')
    # This exact unprofiled TU warning also occurred in the successful pinned
    # O2 control build. Permit only that line/count, with that original log as
    # evidence. Mismatched hashes, stale/corrupt data and every other profile
    # warning remain fatal. No compiler warning/optimization flags are altered.
    require(sha(CONTROL_BUILD_LOG) == CONTROL_BUILD_LOG_SHA, 'Control warning evidence changed')
    control_log = CONTROL_BUILD_LOG.read_text()
    require(BASELINE_SHA in control_log and control_log.splitlines().count(KNOWN_PROFILE_WARNING) == 1,
            'Control log does not prove the exact preexisting profile warning')
    issues = [line for line in log.splitlines() if re.search(
        r'error:|FAILED:|(?:warning:).*(?:profile|profdata)|(?:profile|profdata).*(?:mismatch|out.of.date|malformed|corrupt)',
        line, re.IGNORECASE)]
    accepted = [line for line in issues if line == KNOWN_PROFILE_WARNING]
    require(len(accepted) <= 1, 'Repeated unprofiled warning exceeds the control count')
    issues = [line for line in issues if line != KNOWN_PROFILE_WARNING]
    require(not issues, 'Profile diagnostic invalidates candidate:\n' + '\n'.join(issues[:20]))
    manifest['accepted_preexisting_profile_warnings'] = accepted
    manifest['control_build_log_sha256'] = CONTROL_BUILD_LOG_SHA
    manifest['build_log_sha256'] = sha(output / 'build.log')
    validate_pins()
    require(sha(output / 'module_tables.inc') == manifest['module_tables_sha256'],
            'Generated module tables differ from control')
    for entry in manifest['source_stamps']:
        stat = Path(entry['path']).stat()
        require((stat.st_size, stat.st_mtime_ns) == (entry['size'], entry['mtime_ns']),
                'Source changed during build: ' + entry['path'])
    manifest['candidate_sha256'] = sha(output / MODULE)
    manifest['status'] = 'built; not installed or measured'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    logged(['xcrun', 'vtool', '-show-build', str(output / MODULE)], output / 'platform.txt')
    print('Candidate SHA256: ' + manifest['candidate_sha256'])


if __name__ == '__main__':
    main()
