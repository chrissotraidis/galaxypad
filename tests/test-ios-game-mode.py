#!/usr/bin/env python3
"""Reject stale packaged plists, including keys with incorrect plist types."""
import plistlib
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'scripts/check-ios-game-mode.py'
source = plistlib.loads((ROOT/'apple/ios/Info.plist.in').read_bytes())
with tempfile.TemporaryDirectory(prefix='galaxypad-game-mode-') as temp:
    path = Path(temp)/'Info.plist'
    def check(info, valid):
        path.write_bytes(plistlib.dumps(info))
        result = subprocess.run(['python3',str(SCRIPT),str(path)],capture_output=True,text=True)
        assert (result.returncode == 0) == valid, result.stdout+result.stderr
    check(source,True)
    for key in ('GCSupportsGameMode','LSSupportsGameMode','UIRequiresFullScreen',
                'LSApplicationCategoryType'):
        info=dict(source);del info[key];check(info,False)
        for value in (False,1,'true'):
            check(dict(source,**{key:value}),False)
print('Packaged Game Mode metadata: valid, stale, disabled and wrong-type cases pass')
