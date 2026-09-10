// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadStickRouting.h"
#include <cassert>
#include <limits>
int main() {
  galaxypad::InputState state;
  state.buttons = galaxypad::A; state.pointerVisible = true;
  galaxypad::routeStick(state, 0.5, -0.25, false, 2, true);
  assert(state.moveX == 0.5 && state.moveY == -0.25 && state.tiltX == 0 && state.tiltY == 0);
  galaxypad::routeStick(state, 0.5, -0.25, true, 2, true);
  assert(state.moveX == 0 && state.moveY == 0 && state.tiltX == 1 && state.tiltY == 0.5);
  galaxypad::routeStick(state, 0, 0, false, 1, false);
  assert(state.moveX == 0 && state.moveY == 0 && state.tiltX == 0 && state.tiltY == 0);
  assert(state.buttons == galaxypad::A && state.pointerVisible);
  galaxypad::routeStick(state, std::numeric_limits<float>::quiet_NaN(), 20, true, 100, false);
  assert(state.tiltX == 0 && state.tiltY == 1);
}
