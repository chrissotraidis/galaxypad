#include "../apple/shared/GalaxyPadInput.h"
#include <cassert>
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
  puts("Galaxy mobile input: latches, axes, ownership, consumption-time mapping expiry and clear pass");
}
