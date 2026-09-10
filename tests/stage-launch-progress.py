"""Stage and syntax-check startup UI against the actual cached frontend flags."""
from pathlib import Path
import hashlib
import json
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
build = root/'generated/build/moderngekko-desktop'
source = root/'ref/ModernGekko/tools/moderngekko_launcher.cpp'
before = hashlib.sha256(source.read_bytes()).hexdigest()
text = source.read_text()
old = '        SDL_HideWindow(window);\n        int exit_code = 1;'
assert text.count(old) == 1
fragment = (root/'patches/experiments/frontend-launch-progress.inc').read_text()
text = text.replace(old, fragment+'\n        int exit_code = 1;')
anchor = '          SDL_PumpEvents();\n          SDL_Delay(50);'
assert text.count(anchor) == 1
text = text.replace(anchor, '''          SDL_Event launch_event;
          while (SDL_PollEvent(&launch_event)) {
            ImGui_ImplSDL3_ProcessEvent(&launch_event);
            if (!stop_requested && (launch_event.type == SDL_EVENT_QUIT ||
                (launch_event.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED &&
                 launch_event.window.windowID == SDL_GetWindowID(window)))) {
              stop_requested = true;
              SDL_KillProcess(process, false);
            }
          }
          update_launch_progress();
          SDL_Delay(50);''')
out = root/'generated/frontend-progress-r454'; out.mkdir(exist_ok=False)
staged = out/source.name; staged.write_text(text)
db = json.loads(subprocess.check_output(['ninja', '-t', 'compdb', '-x'], cwd=build))
entry = next(e for e in db if e.get('file') == str(source))
args = shlex.split(entry['command'])
args[args.index('-c')+1] = str(staged)
for flag, value in [('-o', 'frontend.o'), ('-MF', 'frontend.d'), ('-MT', 'frontend.o')]:
    if flag in args: args[args.index(flag)+1] = str(out/value)
args += ['-I'+str(source.parent), '-fsyntax-only']
result = subprocess.run(args, cwd=build, capture_output=True, text=True)
(out/'compiler.log').write_text(result.stdout+result.stderr)
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
(out/'report.json').write_text(json.dumps({'source_sha256': before,
    'command': args, 'exit_code': result.returncode,
    'boundary': 'Staged syntax check only; no package or UI acceptance.'}, indent=2)+'\n')
print(result.stdout+result.stderr)
result.check_returncode()
