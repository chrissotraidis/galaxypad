#include <assert.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
typedef uint32_t (*Probe)(uint32_t, uint32_t);
int main(int argc, char** argv) {
  assert(argc == 3);
  void* first = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
  if (!first) { fprintf(stderr, "%s\n", dlerror()); return 1; }
  void* second = dlopen(argv[2], RTLD_NOW | RTLD_LOCAL);
  if (!second) { fprintf(stderr, "%s\n", dlerror()); return 1; }
  Probe a = (Probe)dlsym(first, "galaxypad_aot_link_probe");
  Probe b = (Probe)dlsym(second, "galaxypad_aot_link_probe");
  assert(a && b && a != b);
  uint32_t state = 0x12345678;
  for (unsigned i = 0; i < 100000; ++i) {
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    uint32_t x = state;
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    uint32_t y = state;
    assert(a(x, y) == ((x + y) * 3u ^ 0x1234u));
    assert(b(x, y) == ((x + y) * 3u ^ 0x5678u));
  }
  puts("200000 calls through two separately linked/load-addressed helper bindings passed");
  assert(dlclose(second) == 0);
  assert(dlclose(first) == 0);
}
