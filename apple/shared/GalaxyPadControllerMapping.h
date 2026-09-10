// SPDX-License-Identifier: GPL-3.0-or-later
// SunPad fcdc1411 controller-mapping mechanism: bijective assignments, swaps
// and invalid-store fallback. Galaxy actions/physical triggers differ.
#pragma once
#include "GalaxyPadInput.h"
#include <array>
namespace galaxypad {
struct ControllerMapping {
  // Game actions A, B, Spin, C, Z -> physical A, B, X, Y, Left Trigger.
  std::array<unsigned,5> physical{0,1,2,3,4};
  bool valid() const {
    unsigned seen=0;
    for (unsigned value:physical) {
      if (value>=5 || (seen&(1u<<value))) return false;
      seen|=1u<<value;
    }
    return seen==31;
  }
  ControllerMapping assigning(unsigned game, unsigned button) const {
    ControllerMapping out=valid()?*this:ControllerMapping{};
    if (game>=5 || button>=5) return out;
    for (auto& value:out.physical) {
      if (value==button) { value=out.physical[game]; break; }
    }
    out.physical[game]=button;
    return out;
  }
  uint32_t apply(unsigned pressed) const {
    const auto map=valid()?*this:ControllerMapping{};
    constexpr uint32_t actions[]={A,B,Spin,C,Z};
    uint32_t result=0;
    for (unsigned i=0;i<5;++i) if (pressed&(1u<<map.physical[i])) result|=actions[i];
    return result;
  }
};
}
