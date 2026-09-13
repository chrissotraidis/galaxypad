// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "apple/shared/GalaxyPadPointerContext.h"
#include "apple/shared/GalaxyPadPointerModel.h"
#include <cstdint>
#include <optional>

namespace galaxypad::experimental {
// Simulator opt-in only. This is a permission to invert neutral coordinates,
// not a gameplay acceptance claim. Caller must report every motion event,
// including latched Spin taps, rather than only currently held buttons.
struct NeutralGameplaySnapshot {
  bool exactDolVerified=false, pitch20ProfileVerified=false;
  bool controllerAim=false, motionActiveOrLatched=false;
  std::uint64_t currentField=0, observationField=0;
  std::optional<PointerContext> context;
  std::optional<PointerCalibration> calibration;
  std::optional<PointerConversionInputs> conversion;
};

class NeutralGameplayReadiness {
public:
  explicit NeutralGameplayReadiness(bool retainNeutralBase=false): retainNeutralBase(retainNeutralBase) {}
  // Three seconds of uninterrupted neutral observations at 60 fields/second.
  // Temporal tracking still exists; this avoids trusting one post-Spin sample.
  static constexpr std::uint64_t SettleFields=180, MaximumAgeFields=4;
  void reset() { neutralSince.reset(); lastField.reset(); controller=0; neutralEstablished=false; }

  std::optional<MenuPointerConfiguration> observe(const NeutralGameplaySnapshot& s) {
    auto near=[](float a,float b) { return std::isfinite(a) && std::abs(a-b)<.0001f; };
    if (!s.exactDolVerified || !s.pitch20ProfileVerified || s.controllerAim ||
        s.motionActiveOrLatched || s.observationField>s.currentField ||
        s.currentField-s.observationField>MaximumAgeFields || !s.context ||
        !s.context->controller || s.context->mode!=25 || !s.calibration || !s.conversion) {
      reset(); return std::nullopt;
    }
    const auto& c=*s.calibration;
    const auto& p=*s.conversion;
    if (!near(c.centerX,0) || !near(c.centerY,-.2f) || !near(c.scale,2.272727f) ||
        !near(c.playRadius,.03f) || !near(c.sensitivity,.5f) || c.filterMode!=0 ||
        !std::isfinite(p.referenceHorizon[0]) || !std::isfinite(p.referenceHorizon[1]) ||
        !std::isfinite(p.accelerationHorizon[0]) || !std::isfinite(p.accelerationHorizon[1])) {
      reset(); return std::nullopt;
    }
    // Discontinuities restart the neutral window. Repeated observations cannot
    // manufacture elapsed time; callers must feed fresh field observations.
    if (!lastField || s.observationField<*lastField ||
        s.observationField-*lastField>MaximumAgeFields || controller!=s.context->controller) {
      neutralSince=s.observationField;
      neutralEstablished=false;
    }
    const bool neutral=near(p.referenceHorizon[0],1) && near(p.referenceHorizon[1],0) &&
      near(p.accelerationHorizon[0],0) && near(p.accelerationHorizon[1],-1);
    // Candidate2 retains a previously established neutral Point base through
    // independent shake motion. It does not predict the instantaneous cursor.
    // Caller must still invalidate explicit tilt and controller takeover.
    if(!neutral && !(retainNeutralBase && neutralEstablished)) {
      reset(); return std::nullopt;
    }
    lastField=s.observationField;
    controller=s.context->controller;
    if (s.observationField-*neutralSince<SettleFields) return std::nullopt;
    neutralEstablished=true;
    return MenuPointerConfiguration{25,20,.1f,{c.centerX,c.centerY},c.scale,true};
  }
private:
  std::optional<std::uint64_t> neutralSince,lastField;
  std::uint32_t controller=0;
  bool retainNeutralBase=false,neutralEstablished=false;
};
} // namespace galaxypad::experimental
