// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411 SunPadInputMixer.{h,mm}: gameplay-source locking,
// rising-edge latching and strongest-axis mixing. Gyro is a pointer-only source.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <mutex>
#include <functional>
#include <optional>
#include <utility>

namespace galaxypad {
// Logical actions, deliberately not GameCube or raw Wii report bit positions.
enum Button : uint32_t {
  A=1u<<0, B=1u<<1, C=1u<<2, Z=1u<<3, Plus=1u<<4, Minus=1u<<5,
  Spin=1u<<6, Up=1u<<7, Down=1u<<8, Left=1u<<9, Right=1u<<10,
  One=1u<<11, Two=1u<<12, Home=1u<<13
};
enum class TiltMode { Normal, RaySurfing, StarBall };
struct InputState {
  uint32_t buttons=0;
  float moveX=0, moveY=0, tiltX=0, tiltY=0;
  float pointerX=0.5f, pointerY=0.5f; // normalized gameplay viewport, top-left origin
  bool pointerVisible=false, connected=false;
  bool upright=false; // emulated Wii Remote pose, independent of held input
  bool pointerContact=false; // touch is down; visibility may persist after lift
};
enum class InputSource { Touch, Controller, Gyro };

class InputMixer {
public:
  using TouchPointerMapper=std::function<std::optional<std::pair<float,float>>(
    const InputState&,const InputState&)>;
  // Installed before input starts. Evaluated at consumption, so a stationary
  // held touch cannot retain mapping after its runtime snapshot expires.
  void setTouchPointerMapper(TouchPointerMapper mapper) {
    std::lock_guard lock(mutex_);
    touchPointerMapper_=std::move(mapper);
  }
  void setTiltMode(TiltMode mode) {
    std::lock_guard lock(mutex_);
    tiltMode_=mode;
    states_[0]={}; states_[1]={}; states_[2]={}; latched_[0]=latched_[1]=latched_[2]=0;
  }
  void set(InputSource source, InputState state) {
    std::lock_guard lock(mutex_);
    auto i=index(source);
    state.moveX=axis(state.moveX); state.moveY=axis(state.moveY);
    state.tiltX=axis(state.tiltX); state.tiltY=axis(state.tiltY);
    if (!std::isfinite(state.pointerX) || !std::isfinite(state.pointerY))
      state.pointerVisible=false;
    state.pointerX=coordinate(state.pointerX); state.pointerY=coordinate(state.pointerY);
    latched_[i] |= state.buttons & ~states_[i].buttons;
    states_[i]=state;
  }
  void clear(InputSource source) {
    std::lock_guard lock(mutex_);
    states_[index(source)]={}; latched_[index(source)]=0;
  }
  // Native menu/lifecycle/ownership transitions clear held AND unconsumed edges.
  void clearAll() {
    std::lock_guard lock(mutex_);
    states_[0]={}; states_[1]={}; states_[2]={}; latched_[0]=latched_[1]=latched_[2]=0;
  }
  // Diagnostics only: observe published input without consuming button edges,
  // running the mapper, or changing controller/touch ownership.
  std::pair<InputState,InputState> diagnosticSnapshot() {
    std::lock_guard lock(mutex_);
    return {states_[0],states_[1]};
  }
  InputState consume() {
    std::lock_guard lock(mutex_);
    auto t=states_[0]; const auto& c=states_[1];
    InputState out;
    out.buttons=t.buttons|c.buttons|latched_[0]|latched_[1];
    out.moveX=strongest(t.moveX,c.moveX); out.moveY=strongest(t.moveY,c.moveY);
    out.tiltX=strongest(t.tiltX,c.tiltX); out.tiltY=strongest(t.tiltY,c.tiltY);
    if(touchPointerMapper_) {
      auto mapped=touchPointerMapper_(t,out);
      if(t.pointerVisible) {
      if(mapped && std::isfinite(mapped->first) && std::isfinite(mapped->second) &&
         mapped->first>=0 && mapped->first<=1 && mapped->second>=0 && mapped->second<=1) {
        t.pointerX=mapped->first;t.pointerY=mapped->second;
      } else t.pointerVisible=false;
      }
    }
    // A finger owns aim while down. After lift, return to visible controller
    // aim; retain touch aim when no controller pointer is available so touch
    // users can aim first and press A/B separately.
    // Gyro is pointer-only. A held touch wins; remembered touch/controller aim
    // cannot mask live gyro. Unavailable gyro leaves the original fallback.
    const auto& gyro=states_[2];
    const auto& fallback=gyro.pointerVisible ? gyro : c;
    const auto& pointer=t.pointerVisible && (t.pointerContact || !fallback.pointerVisible)?t:fallback;
    out.pointerVisible=pointer.pointerVisible;
    out.pointerX=pointer.pointerX; out.pointerY=pointer.pointerY;
    out.connected=t.connected||c.connected;
    if (tiltMode_!=TiltMode::Normal) {
      // Dedicated tilt and the main stick share the selected ride pose.
      const float x=strongest(out.moveX,out.tiltX);
      const float y=strongest(out.moveY,out.tiltY);
      out.moveX=out.moveY=0;
      out.pointerVisible=false;
      out.pointerX=out.pointerY=0.5f;
      out.upright=tiltMode_==TiltMode::StarBall;
      // Dolphin's profile uses 85 degrees at full input. Surf tutorial needs
      // |accel.x| >= .65; 60 degrees clears it without an upside-down pose.
      // The ball sensor centers pitch at 10 degrees, with a 25-degree range.
      out.tiltX=x*(out.upright ? 25.f : 60.f)/85.f;
      out.tiltY=out.upright ? (10.f+25.f*y)/85.f : 0;
    }
    latched_[0]=latched_[1]=latched_[2]=0;
    return out;
  }
private:
  static unsigned index(InputSource source) { return source==InputSource::Touch?0:source==InputSource::Controller?1:2; }
  static float axis(float value) { return std::isfinite(value)?std::clamp(value,-1.f,1.f):0.f; }
  static float coordinate(float value) { return std::isfinite(value)?std::clamp(value,0.f,1.f):0.5f; }
  static float strongest(float touch,float controller) { return std::abs(controller)>std::abs(touch)?controller:touch; }
  std::mutex mutex_;
  InputState states_[3]{};
  uint32_t latched_[3]{};
  TouchPointerMapper touchPointerMapper_;
  TiltMode tiltMode_=TiltMode::Normal;
};
} // namespace galaxypad
