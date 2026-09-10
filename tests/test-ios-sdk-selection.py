"""Reject unknown SDKs before any configure, build, provisioning or data lookup."""
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
for name in ('build-ios-simulator-core.sh', 'build-ios-simulator-module.sh',
             'build-ios-simulator-app.sh', 'provision-ios-simulator-core.sh',
             'stage-private-ios-device.sh'):
    script = root / 'scripts' / name
    subprocess.run(['bash', '-n', str(script)], check=True)
    for value in ('macosx', '../iphoneos', ' '):
        result = subprocess.run(['bash', str(script)], capture_output=True, text=True,
                                env=dict(os.environ, GALAXYPAD_IOS_SDK=value))
        assert result.returncode == 2, (name, value, result.stderr)
        assert result.stderr.strip() == 'GALAXYPAD_IOS_SDK must be iphonesimulator or iphoneos'
        assert not result.stdout
print('All five iOS SDK entry points reject unsupported targets before work')
