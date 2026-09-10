#!/usr/bin/env python3
"""Compile reference-emitter output as immutable Mach-O text; no executable allocation.

Transport prerequisite only: no PPC analysis, register allocator, state adapter,
memory callbacks or cycle/exception equivalence is tested by this probe.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
vendor = root / 'ref/ModernGekko/vendor/dolphin'
emitter = vendor / 'Source/Core/Common/Arm64Emitter.cpp'
def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)

with tempfile.TemporaryDirectory(prefix='galaxypad-arm64-static-') as temp:
    work = Path(temp)
    export = work / 'export'
    run(['xcrun', 'clang++', '-std=c++23', '-O2', '-arch', 'arm64',
         '-mmacosx-version-min=14.0', '-D_M_ARM_64=1',
         '-I'+str(vendor/'Source/Core'),
         '-I'+str(vendor/'Externals/fmt/fmt/include'),
         str(root/'tests/export-arm64-link-probe.cpp'), str(emitter), '-o', str(export)])
    assembly = run([str(export)], capture_output=True).stdout
    if run([str(export)], capture_output=True).stdout != assembly:
        raise RuntimeError('Export changed between fresh exporter processes')
    source = work/'probe.S'
    source.write_text(assembly)
    obj = work/'probe.o'
    run(['xcrun', 'clang', '-arch', 'arm64', '-mmacosx-version-min=14.0',
         '-c', str(source), '-o', str(obj)])
    relocations = run(['xcrun', 'llvm-objdump', '--macho', '--reloc', str(obj)],
                      capture_output=True).stdout
    if 'BR26' not in relocations or '_galaxypad_aot_probe_helper' not in relocations:
        raise RuntimeError('Missing symbolic ARM64 branch relocation: '+relocations)
    libraries = []
    for index, salt in enumerate(['0x1234u', '0x5678u']):
        library = work/f'probe{index}.dylib'
        run(['xcrun', 'clang', '-arch', 'arm64', '-dynamiclib', '-O2',
             '-mmacosx-version-min=14.0', '-DPROBE_SALT='+salt, str(obj),
             str(root/'tests/arm64-link-probe-helper.c'), '-o', str(library)])
        run(['codesign', '--verify', '--strict', str(library)])
        libraries.append(str(library))
    driver = work/'driver'
    run(['xcrun', 'clang', '-arch', 'arm64', '-O2',
         '-mmacosx-version-min=14.0',
         str(root/'tests/arm64-link-probe-driver.c'), '-o', str(driver)])
    result = run([str(driver), *libraries], capture_output=True).stdout
    mobile_objects = {}
    for sdk, target in [('iphonesimulator', 'arm64-apple-ios16.0-simulator'),
                        ('iphoneos', 'arm64-apple-ios16.0')]:
        sdk_path = run(['xcrun', '--sdk', sdk, '--show-sdk-path'],
                       capture_output=True).stdout.strip()
        mobile_obj = work/(sdk+'.o')
        run(['xcrun', 'clang', '-target', target, '-isysroot', sdk_path,
             '-c', str(source), '-o', str(mobile_obj)])
        build = run(['xcrun', 'vtool', '-show-build', str(mobile_obj)],
                    capture_output=True).stdout
        reloc = run(['xcrun', 'llvm-objdump', '--macho', '--reloc', str(mobile_obj)],
                    capture_output=True).stdout
        expected = 'IOSSIMULATOR' if sdk == 'iphonesimulator' else 'IOS'
        if not any(line.strip() == 'platform '+expected for line in build.splitlines()):
            raise RuntimeError('Wrong mobile platform: '+build)
        if 'BR26' not in reloc or '_galaxypad_aot_probe_helper' not in reloc:
            raise RuntimeError('Mobile helper relocation missing')
        mobile_objects[sdk] = dict(build=build, relocations=reloc)
    print(json.dumps(dict(emitter_sha256=hashlib.sha256(emitter.read_bytes()).hexdigest(),
                          assembly=assembly, relocations=relocations,
                          result=result, mobile_objects=mobile_objects,
                          scope=__doc__.strip()), indent=2))
