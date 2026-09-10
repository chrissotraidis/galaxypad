#ifndef GALAXYPAD_EXPERIMENT_DIRECT_TRANSFER_H
#define GALAXYPAD_EXPERIMENT_DIRECT_TRANSFER_H

/* Include after the generated game header. Caller sets LR and target PC first.
 * A true result permits goto to the caller's existing continuation label;
 * false requires immediate return to the chassis, without rewriting PC.
 * Binding changes are permitted only outside guest execution. */
#include "binding.h"

static inline int galaxypad_direct_transfer(CPUState* ctx, uint32_t target,
                                           uint32_t continuation,
                                           void (*callee)(CPUState*))
{
  if (!dolrecomp_call_enter())
    return 0;
  if (!galaxypad_direct_call_boundary(ctx, target))
  {
    dolrecomp_call_leave();
    return 0;
  }

  /* The guard excludes host interception; module replacements are separate.
   * Preserve dolrecomp_call's replacement-before-original ordering. */
  if (!dolrecomp_dispatch_replacement(ctx, target))
    callee(ctx);
  dolrecomp_call_leave();

  if (ctx->pc != continuation ||
      !galaxypad_direct_call_boundary(ctx, continuation))
    return 0;
  if (dolrecomp_dispatch_replacement(ctx, continuation))
    return 0;
  return 1;
}

#endif
