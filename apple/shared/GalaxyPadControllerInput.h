// SPDX-License-Identifier: GPL-3.0-or-later
// Galaxy Wii mapping. SunPad's complete-snapshot/mixer boundary is retained,
// not its GameCube face-button or analog FLUDD trigger assignments.
#pragma once
#include "GalaxyPadInput.h"
#include "GalaxyPadControllerMapping.h"

namespace galaxypad {
struct ControllerSnapshot {
  bool a=false, b=false, x=false, y=false, leftShoulder=false, rightShoulder=false;
  bool leftTrigger=false, rightTrigger=false, menu=false, options=false, recenter=false;
  bool up=false, down=false, left=false, right=false;
  float moveX=0, moveY=0, rightX=0, rightY=0;
};

class ControllerInput {
public:
  void setMapping(ControllerMapping mapping) {
    mapping_=mapping.valid()?mapping:ControllerMapping{}; reset();
  }
  // Menus/lifecycle/ownership changes require release before reactivation.
  void reset() { waitingForNeutral_=true; pointerVisible_=false; x_=y_=0.5f; }
  InputState update(const ControllerSnapshot& pad, float seconds) {
    InputState out;
    float mx=axis(pad.moveX), my=axis(pad.moveY);
    float rx=axis(pad.rightX), ry=axis(pad.rightY);
    bool anyButton=pad.a||pad.b||pad.x||pad.y||pad.leftShoulder||pad.rightShoulder||
      pad.leftTrigger||pad.rightTrigger||pad.menu||pad.options||pad.recenter||
      pad.up||pad.down||pad.left||pad.right;
    if (waitingForNeutral_) {
      if (!anyButton && mx==0 && my==0 && rx==0 && ry==0) waitingForNeutral_=false;
      return out;
    }
    out.connected=true;
    out.buttons=mapping_.apply((pad.a?1u:0)|(pad.b?2u:0)|(pad.x?4u:0)|
                              (pad.y?8u:0)|(pad.leftTrigger?16u:0));
    if (pad.rightTrigger) out.buttons|=B;
    // Duplicate A/B on shoulders so the right thumb can keep aiming IR while
    // confirming, holding a Pull Star, or shooting. Y still supplies camera C.
    if (pad.rightShoulder) out.buttons|=A;
    if (pad.menu) out.buttons|=Plus;
    if (pad.options) out.buttons|=Minus;
    if (pad.up) out.buttons|=Up;
    if (pad.down) out.buttons|=Down;
    if (pad.left) out.buttons|=Left;
    if (pad.right) out.buttons|=Right;
    out.moveX=mx; out.moveY=my;
    if (pad.leftShoulder) {
      // Hold LB to use the right stick for non-motion ball/ray tilt.
      out.tiltX=rx; out.tiltY=ry;
    } else {
      float dt=std::isfinite(seconds)?std::clamp(seconds,0.f,0.05f):0.f;
      if (rx!=0||ry!=0) pointerVisible_=true;
      x_=std::clamp(x_+rx*dt*0.8f,0.f,1.f);
      y_=std::clamp(y_-ry*dt*0.8f,0.f,1.f);
    }
    if (pad.recenter) { x_=y_=0.5f; pointerVisible_=true; }
    out.pointerX=x_; out.pointerY=y_;
    out.pointerVisible=pointerVisible_&&!pad.leftShoulder;
    return out;
  }
private:
  ControllerMapping mapping_;
  static float axis(float value) {
    if (!std::isfinite(value)) return 0;
    value=std::clamp(value,-1.f,1.f);
    constexpr float deadzone=0.15f;
    return std::abs(value)<=deadzone?0:std::copysign((std::abs(value)-deadzone)/(1-deadzone),value);
  }
  bool waitingForNeutral_=true, pointerVisible_=false;
  float x_=0.5f,y_=0.5f;
};
} // namespace galaxypad
