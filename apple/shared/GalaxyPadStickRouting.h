// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "GalaxyPadInput.h"
namespace galaxypad {
inline void routeStick(InputState& state, float x, float y, bool tilt, float sensitivity, bool invertY) {
  auto finiteAxis = [](float value) { return std::isfinite(value) ? std::clamp(value, -1.f, 1.f) : 0.f; };
  state.moveX = state.moveY = state.tiltX = state.tiltY = 0;
  if (tilt) {
    float gain = std::isfinite(sensitivity) ? std::clamp(sensitivity, 0.25f, 2.f) : 1.f;
    state.tiltX = finiteAxis(finiteAxis(x)*gain);
    state.tiltY = finiteAxis(finiteAxis(y)*gain*(invertY ? -1.f : 1.f));
  } else {
    state.moveX = finiteAxis(x); state.moveY = finiteAxis(y);
  }
}
}
