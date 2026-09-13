#include "NeutralGameplayReadiness.h"
#include <cassert>
#include <cstdio>
using namespace galaxypad;
using namespace galaxypad::experimental;
int main() {
  NeutralGameplaySnapshot s;
  s.exactDolVerified=s.pitch20ProfileVerified=true;
  s.context=PointerContext{0x8091f3d8,25};
  s.calibration=PointerCalibration{0,-.2f,2.272727f,.03f,.5f,0};
  s.conversion=PointerConversionInputs{};
  s.conversion->referenceHorizon={1,0};
  s.conversion->accelerationHorizon={0,-1};
  NeutralGameplayReadiness gate;
  auto tick=[&] {s.observationField=s.currentField++; return gate.observe(s);};
  for(unsigned i=0;i<180;++i) assert(!tick());
  assert(tick());
  // A latched tap resets eligibility even if the held button is already gone.
  s.motionActiveOrLatched=true;assert(!tick());
  s.motionActiveOrLatched=false;
  for(unsigned i=0;i<180;++i) assert(!tick());
  assert(tick());
  s.currentField+=10;assert(!tick());
  for(unsigned i=0;i<179;++i) assert(!tick());
  assert(tick());
  s.controllerAim=true;assert(!tick());s.controllerAim=false;
  s.context->mode=5;assert(!tick());s.context->mode=25;
  s.calibration->scale=NAN;assert(!tick());s.calibration->scale=2.272727f;
  s.conversion->accelerationHorizon={.01f,-1};assert(!tick());
  s.conversion->accelerationHorizon={0,-1};
  for(unsigned i=0;i<180;++i) assert(!tick());
  assert(tick());
  s.observationField=s.currentField-10;assert(!gate.observe(s));
  s.observationField=s.currentField+1;assert(!gate.observe(s));
  s.observationField=s.currentField;
  for(unsigned i=0;i<500;++i) assert(!gate.observe(s));
  // Repeating a snapshot does not advance the settle timer.
  s.exactDolVerified=false;assert(!tick());s.exactDolVerified=true;
  s.pitch20ProfileVerified=false;assert(!tick());s.pitch20ProfileVerified=true;
  for(unsigned i=0;i<180;++i) assert(!tick());
  assert(tick());
  s.context->controller+=4;assert(!tick());
  // Candidate2 can retain an established neutral Point base across shake
  // horizons, but cannot establish one from a moving/unknown pose.
  NeutralGameplayReadiness retained(true);
  s.conversion->accelerationHorizon={.3f,-.9f};
  auto step=[&] {s.observationField=s.currentField++; return retained.observe(s);};
  for(unsigned i=0;i<200;++i) assert(!step());
  s.conversion->accelerationHorizon={0,-1};
  for(unsigned i=0;i<180;++i) assert(!step());
  assert(step());
  s.conversion->referenceHorizon={.98f,.1f};
  s.conversion->accelerationHorizon={.3f,-.9f};
  for(unsigned i=0;i<300;++i) assert(step());
  s.calibration->centerY=.2f;assert(!step());s.calibration->centerY=-.2f;
  assert(!step()); // Changed calibration discards the previously known base.
  s.conversion->referenceHorizon={1,0};s.conversion->accelerationHorizon={0,-1};
  for(unsigned i=0;i<180;++i) assert(!step());
  assert(step());
  s.motionActiveOrLatched=true;assert(!step());s.motionActiveOrLatched=false;
  for(unsigned i=0;i<180;++i) assert(!step());
  assert(step());
  s.controllerAim=true;assert(!step());s.controllerAim=false;
  for(unsigned i=0;i<180;++i) assert(!step());
  assert(step());
  s.context->mode=5;assert(!step());s.context->mode=25;
  for(unsigned i=0;i<180;++i) assert(!step());
  assert(step());
  s.currentField+=10;assert(!step());
  puts("Candidate2 retained base: moving pose cannot establish; shake horizons retain only established base; calibration, explicit tilt, controller, context and freshness invalidate");
  puts("Experimental neutral gameplay gate: settle, latched motion, stale/future/repeated observations, context, calibration, horizons and profile checks passed");
}
