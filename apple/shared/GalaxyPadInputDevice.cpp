// SPDX-License-Identifier: GPL-3.0-or-later
#include "GalaxyPadInputDevice.h"
#include "GalaxyPadMovementTrace.h"
#include <functional>
#include <utility>
#if defined(__APPLE__)
#include <TargetConditionals.h>
#if TARGET_OS_SIMULATOR
#include <os/log.h>
#endif
#endif

namespace galaxypad {
namespace {
class Device final : public ciface::Core::Device {
  class Value final : public Input {
  public:
    Value(Device& device, std::string name, std::function<double(const InputState&)> read)
        : device_(device), name_(std::move(name)), read_(std::move(read)) {}
    std::string GetName() const override { return name_; }
    ControlState GetState() const override {
      std::lock_guard lock(device_.mutex_);
      return read_(device_.state_);
    }
  private:
    Device& device_;
    std::string name_;
    std::function<double(const InputState&)> read_;
  };
public:
  explicit Device(std::shared_ptr<InputMixer> mixer) : mixer_(std::move(mixer)) {
    for (auto [name, bit] : {std::pair{"A", A}, {"B", B}, {"C", C}, {"Z", Z},
         {"Plus", Plus}, {"Minus", Minus}, {"Spin", Spin}, {"Up", Up},
         {"Down", Down}, {"Left", Left}, {"Right", Right}, {"One", One}, {"Two", Two}})
      add(name, [bit](const InputState& s) { return (s.buttons & bit) ? 1.0 : 0.0; });
    add("Upright", [](const InputState& s) { return s.upright ? 1.0 : 0.0; });
    axis("MoveX", &InputState::moveX);
    axis("MoveY", &InputState::moveY);
    axis("TiltX", &InputState::tiltX);
    axis("TiltY", &InputState::tiltY);
    add("PointerLeft", [](const InputState& s) { return std::max(0.f, 1-2*s.pointerX); });
    add("PointerRight", [](const InputState& s) { return std::max(0.f, 2*s.pointerX-1); });
    add("PointerUp", [](const InputState& s) { return std::max(0.f, 1-2*s.pointerY); });
    add("PointerDown", [](const InputState& s) { return std::max(0.f, 2*s.pointerY-1); });
    add("PointerHidden", [](const InputState& s) { return s.pointerVisible ? 0.0 : 1.0; });
  }
  std::string GetName() const override { return "Mobile"; }
  std::string GetSource() const override { return "GalaxyPad"; }
  std::optional<int> GetPreferredId() const override { return 0; }
  ciface::Core::DeviceRemoval UpdateInput() override {
    std::lock_guard lock(mutex_);
    state_ = mixer_->consume();
#if defined(__APPLE__) && TARGET_OS_SIMULATOR
    if (state_.buttons != lastLoggedButtons_) {
      os_log_info(OS_LOG_DEFAULT, "[GalaxyPad input device] consumed buttons=%u pointer_visible=%d pointer=(%.3f,%.3f) connected=%d",
        state_.buttons, state_.pointerVisible, state_.pointerX, state_.pointerY, state_.connected);
      lastLoggedButtons_ = state_.buttons;
    }
#endif
    movementTrace_.record(state_.moveX,state_.moveY);
    return ciface::Core::DeviceRemoval::Keep;
  }
private:
  void add(std::string name, std::function<double(const InputState&)> read) {
    AddInput(new Value(*this, std::move(name), std::move(read)));
  }
  void axis(const std::string& name, float InputState::*member) {
    add(name+"+", [member](const InputState& s) { return std::max(0.f, s.*member); });
    add(name+"-", [member](const InputState& s) { return std::max(0.f, -(s.*member)); });
  }
  std::shared_ptr<InputMixer> mixer_;
  std::mutex mutex_;
  InputState state_;
#if defined(__APPLE__) && TARGET_OS_SIMULATOR
  uint32_t lastLoggedButtons_ = 0;
#endif
  MovementTrace movementTrace_{"device"};
};
}
std::shared_ptr<ciface::Core::Device> makeInputDevice(std::shared_ptr<InputMixer> mixer) {
  return std::make_shared<Device>(std::move(mixer));
}
// HOME stays native; deliberately do not bind the retail dynamic HOME RSO.
const char* const mobileWiimoteConfig = R"ini([Wiimote1]
Device = GalaxyPad/0/Mobile
Buttons/A = `A`
Buttons/B = `B`
Buttons/1 = `One`
Buttons/2 = `Two`
Buttons/+ = `Plus`
Buttons/- = `Minus`
D-Pad/Up = `Up`
D-Pad/Down = `Down`
D-Pad/Left = `Left`
D-Pad/Right = `Right`
IR/Up = `PointerUp`
IR/Down = `PointerDown`
IR/Left = `PointerLeft`
IR/Right = `PointerRight`
IR/Hide = `PointerHidden`
Shake/X = `Spin`
Shake/Y = `Spin`
Shake/Z = `Spin`
Hotkeys/Upright Hold = `Upright`
Tilt/Angle = 85
Tilt/Left = `TiltX-`
Tilt/Right = `TiltX+`
Tilt/Forward = `TiltY+`
Tilt/Backward = `TiltY-`
Extension = Nunchuk
Nunchuk/Buttons/C = `C`
Nunchuk/Buttons/Z = `Z`
Nunchuk/Stick/Up = `MoveY+`
Nunchuk/Stick/Down = `MoveY-`
Nunchuk/Stick/Left = `MoveX-`
Nunchuk/Stick/Right = `MoveX+`
Nunchuk/Stick/Calibration = 100 100 100 100 100 100 100 100
Options/Sideways Wiimote = False

[Wiimote2]
[Wiimote3]
[Wiimote4]
)ini";
}
