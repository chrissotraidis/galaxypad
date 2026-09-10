// Private offline emitter/link transport probe. Not a PPC block compiler.
#include "Common/Arm64Emitter.h"
#include "Common/MsgHandler.h"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>

// Keep reference emitter assertions fatal in this console-only tool.
namespace Common {
bool MsgAlertFmtImpl(bool, MsgType, Log::LogType, const char* file, int line,
                     fmt::string_view, const fmt::format_args&) {
  std::fprintf(stderr, "Emitter assertion: %s:%d\n", file, line);
  std::abort();
}
}

int main() {
  using namespace Arm64Gen;
  using enum ARM64Reg;
  // Ordinary writable data, never executable and never passed to a function pointer.
  alignas(16) std::array<u8, 128> storage{};
  ARM64XEmitter emitter(storage.data(), storage.data() + storage.size());
  emitter.STP(IndexType::Pre, X29, X30, SP, -16);
  emitter.ADD(X29, SP, 0u);
  emitter.ADD(W0, W0, W1);
  const auto helper_offset = emitter.GetCodePtr() - storage.data();
  auto branch = emitter.BL();
  emitter.SetJumpTarget(branch); // Placeholder is replaced with a symbolic relocation.
  emitter.LDP(IndexType::Post, X29, X30, SP, 16);
  emitter.RET();
  if (emitter.HasWriteFailed()) return 1;
  const auto length = emitter.GetCodePtr() - storage.data();
  std::puts(".text\n.p2align 2\n.globl _galaxypad_aot_link_probe\n_galaxypad_aot_link_probe:");
  for (std::ptrdiff_t offset = 0; offset < length; offset += 4) {
    if (offset == helper_offset) {
      std::puts("  bl _galaxypad_aot_probe_helper");
    } else {
      u32 word;
      std::memcpy(&word, storage.data() + offset, sizeof(word));
      std::printf("  .long 0x%08x\n", word);
    }
  }
}
