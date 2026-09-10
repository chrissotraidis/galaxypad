"""Separate disposable frontend-test profile; never reuses gameplay logs/saves."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
source = root/'generated/runtime/frontend-acceptance-r447/GalaxyPad'
target = root/'generated/runtime/frontend-progress-r455/GalaxyPad'
target.mkdir(parents=True, exist_ok=False)
shutil.copytree(source/'Config', target/'Config')
for name in ('config.ini', 'default-game.txt'):
    shutil.copy2(source/name, target/name)
assert not (target/'Wii').exists()
print('Use XDG_DATA_HOME='+str(target.parent))
