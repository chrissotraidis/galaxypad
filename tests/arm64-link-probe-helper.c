#include <stdint.h>
#ifndef PROBE_SALT
#error Specify an independent helper binding
#endif
uint32_t galaxypad_aot_probe_helper(uint32_t value) {
  return value * 3u ^ PROBE_SALT;
}
