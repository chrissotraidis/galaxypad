"""Run the actual load flow with state/movie/file stubs, not a live restore test."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/State.cpp').read_text()
flow = source[source.index('static void LoadAsFromCore('):source.index('\nvoid LoadAs(')]
program = r'''
#include <cassert>
#include <cstdio>
#include <filesystem>
#include <functional>
#include <string>
#include <vector>
using u8 = unsigned char;
namespace Common { template<class T> struct UniqueBuffer : std::vector<T> {
  void reset() { std::vector<T>().swap(*this); }
}; }
struct Movie {
  bool active=false, recording=false, playing=false;
  bool IsMovieActive() { return active; }
  bool IsJustStartingRecordingInputFromSaveState() { return recording; }
  bool IsJustStartingPlayingInputFromSaveState() { return playing; }
  void SaveRecording(const std::string&) {}
  void LoadInput(const std::string&) { active=true; }
  void EndPlayInput(bool) { active=false; }
};
namespace Core {
struct System { Movie movie; Movie& GetMovie() { return movie; } };
void DisplayMessage(const std::string&, int) {}
}
namespace File {
bool has_input_recording=false;
std::string GetUserPath(int) { return ""; }
bool Exists(const std::string& path) { return has_input_recording&&path=="checkpoint.dtm"; }
void Delete(const std::string&) {}
}
namespace fmt { template<class... T> std::string format(const char*, T...) { return ""; } }
namespace OSD { struct Duration { static constexpr int NORMAL=1; }; }
constexpr int D_STATESAVES_IDX=0;
struct Worker { void WaitForCompletion() {} } s_compress_and_dump_thread;
Common::UniqueBuffer<u8> s_undo_load_buffer;
std::function<void()> s_on_after_load_callback;
bool readable=true, load_ok=true;
int undo_calls=0;
void SaveToBuffer(Core::System&, Common::UniqueBuffer<u8>& b) { b.resize(128); }
void LoadFileStateData(const std::string&, Common::UniqueBuffer<u8>& b) {
  if(readable) b.resize(16);
}
bool LoadFromBuffer(Core::System&, Common::UniqueBuffer<u8>&) {
  assert(!s_undo_load_buffer.empty()); return load_ok;
}
void UndoLoadState(Core::System&) { assert(!s_undo_load_buffer.empty()); ++undo_calls; }
FLOW
int main() {
  for(int retain=0;retain<2;++retain)
  for(int read=0;read<2;++read)
  for(int success=0;success<2;++success)
  for(int dtm=0;dtm<2;++dtm)
  for(int flags=0;flags<8;++flags) {
    Core::System system;
    system.movie.active=flags&1; system.movie.recording=flags&2; system.movie.playing=flags&4;
    readable=read;load_ok=success;undo_calls=0;s_undo_load_buffer.resize(128);
    File::has_input_recording=dtm;
    bool should_release=!retain&&read&&success&&!dtm&&flags==0;
    int callbacks=0;
    s_on_after_load_callback=[&] {
      ++callbacks;
      assert(s_undo_load_buffer.empty()==should_release);
      // A callback may start a new operation. Its buffer must survive this load.
      s_undo_load_buffer.resize(32);
    };
    LoadAsFromCore(system,"checkpoint",retain);
    assert(callbacks==1&&s_undo_load_buffer.size()==32);
    assert(undo_calls==(read&&!success?1:0));
  }
  Core::System system;
  readable=true;load_ok=true;s_on_after_load_callback={};
  LoadAsFromCore(system,"normal");
  assert(s_undo_load_buffer.size()==128); // Existing callers retain undo by default.
}
'''.replace('FLOW', flow)
with tempfile.TemporaryDirectory(prefix='galaxypad-checkpoint-undo-') as directory:
    cpp = Path(directory) / 'test.cpp'
    binary = Path(directory) / 'test'
    cpp.write_text(program)
    subprocess.run(['clang++', '-std=c++20', '-fsanitize=address,undefined',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Checkpoint undo flow: 128 cases plus default retention pass ASan/UBSan; live test pending')
