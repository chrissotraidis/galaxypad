"""Prepare an isolated app/profile to test new frontend with unchanged game core."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
original = root/'generated/macos/GalaxyPad.app'
candidate = root/'generated/macos/progress-r456/GalaxyPad.app'
candidate.parent.mkdir(exist_ok=False)
shutil.copytree(original, candidate, symlinks=True)
macos = candidate/'Contents/MacOS'
shutil.copy2(root/'generated/frontend-progress-r454/GalaxyPadFrontend', macos/'GalaxyPadFrontend')
subprocess.run(['codesign', '--force', '--sign', '-', str(candidate)], check=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['GalaxyPadRunner', 'gRMGE01_recomp.dylib']:
    assert sha(macos/name) == sha(original/'Contents/MacOS'/name)
profile = root/'generated/runtime/frontend-progress-game-r456/GalaxyPad'
profile.mkdir(parents=True, exist_ok=False)
source = root/'generated/runtime/scale-installed-r390'
for directory in ['Config', 'Wii']:
    shutil.copytree(source/directory, profile/directory)
shutil.copy2(source/'config.ini', profile/'config.ini')
(profile/'default-game.txt').write_text(str(root/'generated/extracted/run1')+'\n')
(profile/'Pipes').mkdir(); os.mkfifo(profile/'Pipes/galaxypad', 0o600)
save = Path('Wii/title/00010000/524d4745/data/GameData.bin')
assert sha(profile/save) == sha(source/save)
(profile.parent/'preparation.json').write_text(json.dumps({
    'app': str(candidate), 'xdg_data_home': str(profile.parent),
    'save_sha256': sha(profile/save), 'boundary': 'Prepared, not executed'}, indent=2)+'\n')
print('Isolated candidate and real-save profile ready; normal app/core/save untouched')
