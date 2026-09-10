"""Preprocess actual host gate; never confuse a launch request with compiled support."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
source = (root/'apple/ios/GalaxyPadCoreHost.mm').read_text()
start = source.index('#if GALAXYPAD_ENABLE_NATIVE_THP', source.index('config.builtin_mods='))
end = source.index('#endif', start) + len('#endif')
gate = source[start:end]
for enabled in (0, 1):
    output = subprocess.check_output(['clang', '-E', '-P', '-x', 'objective-c++',
        '-DGALAXYPAD_ENABLE_NATIVE_THP='+str(enabled), '-'], input=gate, text=True)
    assert ('GalaxyPadTHPModDescriptor()' in output) == bool(enabled)
    assert ('requested but unavailable' in output) == (not enabled)
    assert 'boolForKey:@"GalaxyPadDevNativeTHP"' in output
print('Native THP compile gates: supported registration or explicit unavailable warning passes')
