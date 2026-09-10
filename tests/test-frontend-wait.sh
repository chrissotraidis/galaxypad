#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 - "$root" <<'PY'
import pathlib, subprocess, sys, tempfile
root = pathlib.Path(sys.argv[1])
source = (root / 'ref/ModernGekko/tools/moderngekko_launcher.cpp').read_text()
body = 'int exit_code = 1;' + source.split('        int exit_code = 1;', 1)[1].split('SDL_DestroyProcess(process);', 1)[0]
test = r'''
#include <cassert>
int polls, pumps, delays, mode, events, kills, processed;
constexpr int SDL_EVENT_QUIT = 1, SDL_EVENT_WINDOW_CLOSE_REQUESTED = 2;
struct SDL_Event { int type; struct { int windowID; } window; };
int SDL_GetWindowID(void*) { return 42; }
bool SDL_PollEvent(SDL_Event* event) {
  ++pumps;
  if (mode < 3 || events == 3) return false;
  event->type = mode == 3 ? SDL_EVENT_QUIT : SDL_EVENT_WINDOW_CLOSE_REQUESTED;
  event->window.windowID = mode == 5 ? 99 : 42;
  ++events;
  return true;
}
void ImGui_ImplSDL3_ProcessEvent(SDL_Event*) { ++processed; }
bool SDL_KillProcess(void*, bool force) { assert(!force); ++kills; return true; }
const char* error = "stale unrelated error";
void SDL_ClearError() { error = ""; }
const char* SDL_GetError() { return error; }
bool SDL_WaitProcess(void*, bool block, int* code) {
  assert(!block);
  ++polls;
  if (mode == 2) { error = "monitor failed"; return false; }
  if (polls < 3) return false;
  *code = mode == 1 ? 7 : 0;
  return true;
}
void SDL_Delay(int ms) { assert(ms == 50); ++delays; }
void run() {
  void* process = nullptr;
  void* window = nullptr;
  bool stop_requested = false;
  int updates = 0;
  const auto update_launch_progress = [&] { ++updates; };
''' + body + r'''
  if (mode == 2) {
    assert(!waited && polls == 1 && pumps == 0 && delays == 0);
    assert(*SDL_GetError());
  } else {
    assert(waited && exit_code == (mode == 1 ? 7 : 0));
    assert(polls == 3 && delays == 2 && updates == 2);
    assert(processed == (mode >= 3 ? 3 : 0));
    assert(kills == (mode == 3 || mode == 4 ? 1 : 0));
    assert(stop_requested == (kills == 1));
  }
}
int main() {
  for (mode = 0; mode < 6; ++mode) {
    polls = pumps = delays = events = kills = processed = 0;
    error = "stale unrelated error";
    run();
  }
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-wait-test-') as temporary:
    base = pathlib.Path(temporary)
    (base / 'test.cpp').write_text(test)
    subprocess.run(['c++', '-std=c++17', str(base / 'test.cpp'), '-o', str(base / 'test')], check=True)
    subprocess.run([str(base / 'test')], check=True)
PY
echo "Frontend nonblocking wait tests passed"
