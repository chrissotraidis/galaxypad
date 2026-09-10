#!/usr/bin/env python3
"""Compile the actual depth-peek method against a bounded cache/texture double.

Tests the caller's flush ownership, not Metal completion, cache invalidation,
GPU values, or full PopulateEFBCache semantics.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/FramebufferManager.cpp').read_text()
start = source.index('float FramebufferManager::PeekEFBDepth(u32 x, u32 y)')
end = source.index('\nvoid FramebufferManager::SetEFBCacheTileSize', start)
method = source[start:end]
harness = r'''
#include <cassert>
#include <cstdint>
using u32 = uint32_t;
constexpr u32 EFB_HEIGHT = 528;
struct { bool bUsesLowerLeftOrigin = false; } g_backend_info;
struct Texture {
  int flushes = 0, reads = 0;
  bool pending = false;
  float value = 0.375f;
  u32 x = 0, y = 0;
  void Flush() { ++flushes; pending = false; }
  void ReadTexel(u32 px, u32 py, float* out) {
    assert(!pending); ++reads; x = px; y = py; *out = value;
  }
};
struct FramebufferManager {
  Texture texture;
  struct Cache {
    struct Tile { unsigned frame_access_mask = 0; } tiles[1];
    bool needs_flush = false;
    Texture* readback_texture;
  } m_efb_depth_cache{{}, false, &texture};
  bool present = false;
  int populations = 0;
  bool IsEFBCacheTilePresent(bool depth, u32, u32, u32* tile) {
    assert(depth); *tile = 0; return present;
  }
  // Model only the synchronous-population postcondition from current source.
  void PopulateEFBCache(bool depth, u32 tile) {
    assert(depth && tile == 0); ++populations; present = true;
    texture.pending = true; texture.Flush();
    m_efb_depth_cache.needs_flush = false;
  }
  float PeekEFBDepth(u32 x, u32 y);
};
'''
checks = r'''
int main() {
  FramebufferManager fb;
  assert(fb.PeekEFBDepth(20, 30) == 0.375f);
  assert(fb.populations == 1 && fb.texture.flushes == 1);
  assert(fb.m_efb_depth_cache.tiles[0].frame_access_mask == 1);
  fb.texture.value = 0.625f;
  assert(fb.PeekEFBDepth(21, 31) == 0.625f);
  assert(fb.populations == 1 && fb.texture.flushes == 1);
  // Async refresh has a present tile but its copy has not completed yet.
  fb.m_efb_depth_cache.needs_flush = true;
  fb.texture.pending = true;
  assert(fb.PeekEFBDepth(22, 32) == 0.625f);
  assert(fb.texture.flushes == 2 && !fb.m_efb_depth_cache.needs_flush);
  fb.PeekEFBDepth(23, 33);
  assert(fb.texture.flushes == 2);
  g_backend_info.bUsesLowerLeftOrigin = true;
  fb.PeekEFBDepth(24, 34);
  assert(fb.texture.x == 24 && fb.texture.y == EFB_HEIGHT - 1 - 34);
  assert(fb.texture.reads == 5);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-efb-peek-') as directory:
    path = Path(directory)
    cpp = path / 'peek.cpp'
    cpp.write_text(harness + method + checks)
    binary = path / 'peek'
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-O1', '-g',
                    '-fsanitize=address,undefined', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Actual PeekEFBDepth: one miss flush, no repeated cached flush, async wait once, value and origin forwarding pass')
