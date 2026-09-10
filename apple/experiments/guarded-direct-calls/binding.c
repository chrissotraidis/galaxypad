#include "binding.h"
#include <stddef.h>

static GalaxyPadDirectBoundary s_boundary;

int galaxypad_bind_direct_calls_v1(uint32_t version, GalaxyPadDirectBoundary boundary)
{
  s_boundary = NULL;
  if (version != GALAXYPAD_DIRECT_CALL_BINDING_VERSION)
    return 0;
  s_boundary = boundary;
  return 1;
}

int galaxypad_direct_call_boundary(CPUState* state, uint32_t target)
{
  return state && s_boundary && s_boundary(state, target);
}
