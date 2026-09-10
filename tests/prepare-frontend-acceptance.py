"""Prepare a disposable frontend profile; never launch or modify normal data."""
from pathlib import Path
import hashlib
import json
import shutil

root=Path(__file__).resolve().parents[1]
source=root/'generated/runtime/scale-installed-r390'
out=root/'generated/runtime/frontend-acceptance-r447'
profile=out/'GalaxyPad'
save=Path('Wii/title/00010000/524d4745/data/GameData.bin')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='106e8248bd8081404e8258a7ca33c54e0d476d651f139fde5ee2e4aad7302c90'
assert sha(source/save)==expected
profile.mkdir(parents=True,exist_ok=False)
for name in ('Config','Wii'):
 shutil.copytree(source/name,profile/name)
shutil.copy2(source/'config.ini',profile/'config.ini')
(profile/'default-game.txt').write_text(str(root/'generated/extracted/run1')+'\n')
assert sha(profile/save)==expected and not (profile/'StateSaves').exists()
report={'source':str(source),'profile':str(profile),'xdg_data_home':str(out),
 'save_sha256':expected,'game_path':str(root/'generated/extracted/run1'),
 'frontend':str(root/'generated/macos/GalaxyPad.app/Contents/MacOS/GalaxyPadFrontend'),
 'boundary':'Prepared only. Launch packaged frontend directly with this XDG_DATA_HOME; wrapper overrides it. No import, UI, gameplay, performance or gate acceptance yet.'}
(out/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
