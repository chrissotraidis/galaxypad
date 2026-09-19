#include "../apple/shared/GalaxyPadInput.h"
#include <cassert>
#include <array>
#include <limits>
#include <cstdio>
using namespace galaxypad;
int main() {
  InputMixer mixer;
  assert(mixer.consume().buttons==0 && !mixer.consume().pointerVisible);
  // A neutral connected diagnostic controller must not mask held UIKit axes.
  InputState neutralController; neutralController.connected=true;
  mixer.set(InputSource::Controller,neutralController);
  InputState heldStick; heldStick.connected=true;
  heldStick.moveX=.75f; heldStick.moveY=-.5f;
  mixer.set(InputSource::Touch,heldStick);
  for (unsigned poll=0;poll<120;++poll) {
    const auto held=mixer.consume();
    assert(held.moveX==.75f && held.moveY==-.5f);
  }
  mixer.clear(InputSource::Touch);
  assert(mixer.consume().moveX==0 && mixer.consume().moveY==0);
  // Analog contacts released before polling intentionally do not latch.
  // Do not stretch real movement to compensate for short automated drags.
  mixer.set(InputSource::Touch,heldStick);
  mixer.set(InputSource::Touch,InputState{});
  const auto released=mixer.consume();
  assert(released.moveX==0 && released.moveY==0);
  mixer.clearAll();
  InputState touch; touch.buttons=A|Spin; touch.connected=true;
  mixer.set(InputSource::Touch,touch);
  touch.buttons=0; mixer.set(InputSource::Touch,touch);
  for (unsigned i=0;i<5;++i) {
    auto snapshot=mixer.diagnosticSnapshot();
    assert(snapshot.first.buttons==0 && snapshot.first.connected);
    assert(!snapshot.second.connected);
  }
  assert(mixer.consume().buttons==(A|Spin)); // fast tap survives once
  assert(mixer.consume().buttons==0);
  touch.buttons=A; mixer.set(InputSource::Touch,touch);
  assert(mixer.consume().buttons==A);
  touch.buttons=A|B|Two; mixer.set(InputSource::Touch,touch);
  assert(mixer.consume().buttons==(A|B|Two));
  touch.buttons=B|Two; mixer.set(InputSource::Touch,touch);
  assert(mixer.consume().buttons==(B|Two)); // releasing A preserves other holds
  touch.buttons=0; mixer.set(InputSource::Touch,touch);
  assert(mixer.consume().buttons==0);
  InputState controller; controller.buttons=Z; controller.moveX=-.9f;
  controller.tiltY=.8f; controller.pointerVisible=true; controller.pointerX=.2f;
  mixer.set(InputSource::Controller,controller);
  touch.buttons=B; touch.moveX=.5f; touch.pointerVisible=true; touch.pointerX=.7f;
  touch.pointerContact=true;
  mixer.set(InputSource::Touch,touch);
  auto s=mixer.consume();
  assert(s.buttons==(B|Z) && s.moveX==-.9f && s.tiltY==.8f && s.pointerX==.7f);
  touch.pointerContact=false; mixer.set(InputSource::Touch,touch); s=mixer.consume();
  assert(s.pointerX==.2f && s.buttons==(B|Z)); // lift returns aim, preserves holds
  controller.pointerVisible=false; mixer.set(InputSource::Controller,controller);
  s=mixer.consume(); assert(s.pointerVisible && s.pointerX==.7f); // retained touch aim
  touch.buttons=A; mixer.set(InputSource::Touch,touch); s=mixer.consume();
  assert(s.pointerX==.7f && (s.buttons&A)); // separate A still uses retained touch
  controller.pointerVisible=true; mixer.set(InputSource::Controller,controller);
  mixer.clear(InputSource::Touch); s=mixer.consume();
  assert(s.buttons==Z && s.pointerX==.2f);
  controller.buttons=Spin; mixer.set(InputSource::Controller,controller);
  mixer.clearAll(); s=mixer.consume();
  assert(!s.buttons && !s.pointerVisible && !s.connected && s.moveX==0 && s.tiltY==0);
  touch.moveX=100; touch.moveY=std::numeric_limits<float>::infinity();
  touch.pointerX=std::numeric_limits<float>::quiet_NaN(); touch.pointerVisible=true;
  mixer.set(InputSource::Touch,touch); s=mixer.consume();
  assert(s.moveX==1 && s.moveY==0 && !s.pointerVisible && s.pointerX==.5f);
  mixer.clearAll();
  bool ready=true;unsigned calls=0;uint32_t observedButtons=0;
  mixer.setTouchPointerMapper([&](const InputState& raw,const InputState& merged)
      ->std::optional<std::pair<float,float>> {
    ++calls; observedButtons=merged.buttons;
    if(!ready) return std::nullopt;
    return std::pair{raw.pointerX/2,raw.pointerY/2};
  });
  touch={};touch.pointerVisible=true;touch.pointerX=.8f;touch.pointerY=.6f;
  touch.buttons=A|B;touch.moveX=.4f;
  mixer.set(InputSource::Touch,touch);
  s=mixer.consume();
  assert(s.pointerVisible && s.pointerX==.4f && s.pointerY==.3f &&
    s.buttons==(A|B) && s.moveX==.4f);
  ready=false;s=mixer.consume(); // No new event: held touch expires at consumption.
  assert(!s.pointerVisible && s.buttons==(A|B) && s.moveX==.4f);
  controller={};controller.pointerVisible=true;controller.pointerX=.9f;
  mixer.set(InputSource::Controller,controller);s=mixer.consume();
  assert(s.pointerVisible && s.pointerX==.9f); // Controller coordinates never mapped.
  ready=true;touch.pointerVisible=false;touch.buttons=Spin;
  mixer.set(InputSource::Touch,touch);touch.buttons=0;mixer.set(InputSource::Touch,touch);
  s=mixer.consume();assert(observedButtons==Spin && s.pointerX==.9f);
  mixer.clearAll();s=mixer.consume();assert(!s.pointerVisible && !s.buttons);
  assert(calls>=5); // Hidden/cleared input cannot be resurrected by mapper output.
  // Settled Wii gravity from Dolphin's Rx(upright) * Ry(roll) * Rx(-pitch).
  // Check the game's tutorial predicates, not just that axes were reassigned.
  auto gravity=[](const InputState& state) {
    constexpr float radians=3.14159265358979323846f/180;
    float roll=state.tiltX*85*radians, pitch=state.tiltY*85*radians;
    float x=std::sin(roll)*std::cos(pitch), y=std::sin(pitch);
    float z=std::cos(roll)*std::cos(pitch);
    return state.upright ? std::array<float,3>{x,-z,y} : std::array<float,3>{x,y,z};
  };
  // Mode changes clear held axes and unconsumed presses from both sources.
  touch={};touch.buttons=A;touch.moveX=1;touch.pointerVisible=true;
  mixer.set(InputSource::Touch,touch);
  mixer.setTiltMode(TiltMode::RaySurfing);
  s=mixer.consume();assert(!s.buttons && s.tiltX==0 && !s.upright);
  mixer.set(InputSource::Touch,touch);s=mixer.consume();
  assert(s.buttons==A && s.moveX==0 && s.moveY==0 && !s.pointerVisible);
  assert(std::abs(s.tiltX-60.f/85)<1e-6 && s.tiltY==0);
  auto g=gravity(s);assert(g[0]>=.65f && g[1]>=-.5f);
  controller={};controller.moveX=-1;controller.moveY=1;controller.buttons=Spin;
  mixer.clear(InputSource::Touch);mixer.set(InputSource::Controller,controller);
  s=mixer.consume();assert(s.tiltX<0 && s.tiltY==0 && s.buttons==Spin);
  g=gravity(s);assert(g[0]<=-.65f && g[1]>=-.5f);
  mixer.setTiltMode(TiltMode::StarBall);
  s=mixer.consume();assert(s.upright && s.tiltX==0 && !s.buttons);
  assert(std::abs(s.tiltY-10.f/85)<1e-6); // calibrated resting pose, not forward drift
  g=gravity(s);
  assert(-g[1]>std::cos(30.f*3.14159265f/180)); // upright tutorial within 30 degrees
  assert(std::abs(std::atan2(g[2],-g[1])*180/3.14159265f-10)<.001f);
  mixer.set(InputSource::Controller,controller);s=mixer.consume();
  assert(s.upright && std::abs(s.tiltX+25.f/85)<1e-6);
  assert(std::abs(s.tiltY-35.f/85)<1e-6 && !s.pointerVisible);
  mixer.clearAll();s=mixer.consume();
  assert(s.upright && s.tiltX==0 && !s.buttons); // clearing keeps resting pose
  mixer.setTiltMode(TiltMode::Normal);s=mixer.consume();
  assert(!s.upright && s.tiltY==0);
  mixer.set(InputSource::Controller,controller);s=mixer.consume();
  assert(s.moveX==-1 && s.moveY==1 && s.tiltX==0);
  mixer.clearAll();
  InputState gyro;gyro.pointerVisible=true;gyro.pointerX=.8;gyro.pointerY=.3;
  gyro.buttons=A;gyro.moveX=1; // gyro source is strictly pointer-only
  mixer.set(InputSource::Gyro,gyro);
  controller={};controller.buttons=B;controller.pointerVisible=true;controller.pointerX=.2;
  mixer.set(InputSource::Controller,controller);s=mixer.consume();
  assert(s.pointerX==gyro.pointerX && s.buttons==B && s.moveX==0);
  touch={};touch.pointerVisible=true;touch.pointerContact=true;touch.pointerX=.6;
  mixer.set(InputSource::Touch,touch);s=mixer.consume();
  assert(std::abs(s.pointerX-.3f)<1e-6); // existing mapper still owns touch coordinates
  touch.pointerContact=false;mixer.set(InputSource::Touch,touch);s=mixer.consume();
  assert(s.pointerX==gyro.pointerX); // remembered finger position cannot mask gyro
  mixer.clear(InputSource::Gyro);s=mixer.consume();assert(s.pointerX==controller.pointerX);
  mixer.set(InputSource::Gyro,gyro);mixer.clearAll();s=mixer.consume();
  assert(!s.pointerVisible && !s.buttons);
  mixer.setTiltMode(TiltMode::StarBall);mixer.set(InputSource::Gyro,gyro);s=mixer.consume();
  assert(!s.pointerVisible && s.upright && !s.buttons);
  puts("Galaxy mobile input: latches, axes, ownership, consumption-time mapping expiry and clear pass");
}
