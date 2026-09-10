"""Pinned, unapplied diagnostic selector: default AOT and no mobile JIT path."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = root/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp'
original = source.read_bytes()
assert hashlib.sha256(original).hexdigest() == '4d6a94340dce60254990d9ec7010fe267ba9ff3f366b5e7eef49499f8026e72d'
patch = root/'patches/experiments/macos-reference-jit.patch'
powerpc = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/PowerPC.h').read_text()
enum_start = powerpc.index('enum class CPUCore\n')
enum = powerpc[enum_start:powerpc.index('};', enum_start)+2]
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    copy = base/'src/runtime/dolphin_runtime.cpp'
    copy.parent.mkdir(parents=True)
    copy.write_bytes(original)
    # R557 added canonical built-in descriptors, unrelated to CPU selection.
    # Prove this exact patch accounts for all drift from the original JIT fixture.
    builtin_patch = root/'patches/ModernGekko/0028-builtin-mod-descriptors.patch'
    subprocess.run(['git', 'apply', '--reverse', '--include=src/runtime/dolphin_runtime.cpp',
                    str(builtin_patch)], cwd=base, check=True)
    assert hashlib.sha256(copy.read_bytes()).hexdigest() == '053fa6748d38014b068cb0c097878221d722f226d9cb864d57d1d734f4db5cdb'
    subprocess.run(['git', 'apply', '--include=src/runtime/dolphin_runtime.cpp',
                    str(builtin_patch)], cwd=base, check=True)
    assert copy.read_bytes() == original
    subprocess.run(['git', 'apply', str(patch)], cwd=base, check=True)
    changed = copy.read_text()
    begin = changed.index('#if defined(__APPLE__) && defined(_M_ARM_64) && !defined(MODERNGEKKO_HAVE_IOS)')
    end = changed.index('#endif', begin)+len('#endif')
    block = changed[begin:end]
    subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=base, check=True)
    assert copy.read_bytes() == original
    unit = base/'selector.cpp'
    unit.write_text('#include <cstdio>\n#include <cstdlib>\n#include <string_view>\n'
                    '#ifdef GALAXYPAD_TEST_NONAPPLE\n#undef __APPLE__\n#endif\n'
                    'namespace PowerPC {\n'+enum+'\n}\n'
                    'namespace Config { constexpr int MAIN_CPU_CORE=0;\n'
                    'PowerPC::CPUCore selected;\n'
                    'void SetBase(int, PowerPC::CPUCore c) { selected=c; } }\n'
                    'int main() {\n'+block+'\nreturn static_cast<int>(Config::selected); }\n')
    for name, flags, permitted in [
        ('mac-arm', ['-D__APPLE__=1', '-D_M_ARM_64=1'], True),
        ('ios', ['-D__APPLE__=1', '-D_M_ARM_64=1', '-DMODERNGEKKO_HAVE_IOS=1'], False),
        ('other-os', ['-DGALAXYPAD_TEST_NONAPPLE=1', '-D_M_ARM_64=1'], False),
        ('other-arch', ['-D__APPLE__=1', '-U_M_ARM_64'], False)]:
        exe = base/name
        subprocess.run(['c++', '-std=c++20', '-fsanitize=address,undefined',
                        *flags, str(unit), '-o', str(exe)], check=True)
        for value in (None, '', '0', '1', 'true', '11'):
            env = dict(os.environ)
            env.pop('GALAXYPAD_MACOS_REFERENCE_JIT', None)
            if value is not None:
                env['GALAXYPAD_MACOS_REFERENCE_JIT'] = value
            result = subprocess.run([str(exe)], env=env, capture_output=True, text=True)
            enabled = permitted and value == '1'
            assert result.returncode == (4 if enabled else 6), (name, value, result.stderr)
            if enabled:
                assert 'not mobile/AOT acceptance' in result.stderr
assert source.read_bytes() == original
print('Pinned diagnostic selector: exact opt-in, default AOT, mobile/other-target exclusion, reversible patch pass')
