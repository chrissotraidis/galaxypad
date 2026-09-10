// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "GalaxyPadPointerContext.h"
#include "GalaxyPadPointerModel.h"
namespace galaxypad {
// Exact-DOL gating belongs to the reader. This only recognizes the observed
// stationary file-list/detail states and the explicitly generated22 profile.
// It is permission to model coordinates, never permission to emit A or B.
inline std::optional<MenuPointerConfiguration> MenuPointerReadiness(
    bool verifiedPitch22Profile, const std::optional<PointerContext>& context,
    const std::optional<ActorPointerState>& actor,
    const std::optional<PointerCalibration>& calibration,
    const std::optional<PointerConversionInputs>& conversion) {
  if (!verifiedPitch22Profile || !context || !context->controller || context->mode!=5 || !actor ||
      !actor->spine ||
      (actor->current!=0x806a0114 && actor->current!=0x806a0128) ||
      actor->pending || !calibration || !conversion)
    return std::nullopt;
  auto near=[](float a,float b) {return std::isfinite(a) && std::abs(a-b)<.0001f;};
  const auto& c=*calibration;
  const auto& p=*conversion;
  if (!near(c.centerX,0) || !near(c.centerY,-.2f) || !near(c.scale,2.272727f) ||
      !near(c.playRadius,.03f) || !near(c.sensitivity,.5f) || c.filterMode!=0 ||
      !near(p.referenceHorizon[0],1) || !near(p.referenceHorizon[1],0) ||
      !near(p.accelerationHorizon[0],0) || !near(p.accelerationHorizon[1],-1))
    return std::nullopt;
  return MenuPointerConfiguration{25,22,.1f,{c.centerX,c.centerY},c.scale,true};
}
} // namespace galaxypad
