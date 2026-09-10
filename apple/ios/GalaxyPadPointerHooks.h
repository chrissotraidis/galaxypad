// SPDX-License-Identifier: GPL-3.0-or-later
// Simulator-only diagnostic. Included by CoreHost, never a guest action override.
#pragma once
#include "moderngekko/mod_abi.h"
#include "../shared/GalaxyPadPointerContext.h"
#include <array>
namespace galaxypad {
namespace {
struct PointerHookFrame {
  uint32_t stack, address, actor;
  std::optional<ProcessedPointer> position;
  std::optional<PointerCalibration> calibration;
  std::optional<PointerConversionInputs> conversion;
};
struct PointerHookProbe {
  std::array<PointerHookFrame,16> frames{};
  unsigned depth=0, entries=0, misses=0, hits=0;
  unsigned movements=0;
  std::optional<ProcessedPointer> lastPosition;
  bool invalid=false;
};
bool ObservePointerMovement(PointerHookProbe& probe,
                            const std::optional<ProcessedPointer>& position) {
  if (!position || probe.movements>=32) return false;
  const auto& p=*position;
  if (probe.lastPosition) {
    const auto& previous=*probe.lastPosition;
    if (p.controller==previous.controller && p.pastValid==previous.pastValid &&
        p.currentValid==previous.currentValid &&
        std::abs(p.pastX-previous.pastX)<.01f && std::abs(p.pastY-previous.pastY)<.01f &&
        std::abs(p.currentX-previous.currentX)<.01f && std::abs(p.currentY-previous.currentY)<.01f)
      return false;
  }
  probe.lastPosition=p;
  ++probe.movements;
  return true;
}
// One runtime owns this probe. Load resets before CPU start; only CPU callbacks
// access it while running. Bounded storage and output; no per-query allocation.
PointerHookProbe pointerHookProbe;
void PointerQueryEntry(const CPUState *state) {
  auto& probe=pointerHookProbe;
  if (probe.invalid) return;
  if (probe.depth==probe.frames.size()) { probe.invalid=true; return; }
  auto read=[&](uint32_t address)->std::optional<uint32_t> {
    // ReadProcessedPointer bounds-checks each word before invoking this reader.
    const bool mem2=address>=0x90000000u;
    const auto* bytes=mem2?state->exram:state->ram;
    if (!bytes) return std::nullopt;
    bytes+=address-(mem2?0x90000000u:0x80000000u);
    return (uint32_t(bytes[0])<<24)|(uint32_t(bytes[1])<<16)|
           (uint32_t(bytes[2])<<8)|uint32_t(bytes[3]);
  };
  probe.frames[probe.depth++]={state->gpr[1],state->lr,state->gpr[3],
    ReadProcessedPointer(state->gpr[13],read),ReadPointerCalibration(read),
    ReadPointerConversionInputs(read)};
  if (probe.entries++<4)
    NSLog(@"[GalaxyPad pointer hook] entry actor=%08x return=%08x",state->gpr[3],state->lr);
}
void PointerQueryReturn(const CPUState *state) {
  auto& probe=pointerHookProbe;
  if (probe.invalid || !probe.depth) return;
  const auto frame=probe.frames[probe.depth-1];
  if (frame.stack!=state->gpr[1] || frame.address!=state->pc) {
    probe.invalid=true;
    NSLog(@"[GalaxyPad pointer hook] pairing invalid; observation stopped");
    return;
  }
  --probe.depth;
  const bool hit=state->gpr[3]!=0;
  const bool movement=ObservePointerMovement(probe,frame.position);
  if ((hit && probe.hits++<16) || (!hit && probe.misses++<4) || movement) {
    NSLog(@"[GalaxyPad pointer hook] return actor=%08x result=%u",frame.actor,state->gpr[3]);
    if (frame.position) {
      const auto& p=*frame.position;
      NSLog(@"[GalaxyPad pointer sample] controller=%08x past=(%.3f,%.3f,%d) current=(%.3f,%.3f,%d)",
        p.controller,p.pastX,p.pastY,p.pastValid,p.currentX,p.currentY,p.currentValid);
    }
    if (frame.calibration) {
      const auto& c=*frame.calibration;
      NSLog(@"[GalaxyPad pointer calibration] center=(%.6f,%.6f) scale=%.6f radius=%.6f sensitivity=%.6f mode=%u",
        c.centerX,c.centerY,c.scale,c.playRadius,c.sensitivity,c.filterMode);
    }
    if (frame.conversion) {
      const auto& c=*frame.conversion;
      NSLog(@"[GalaxyPad pointer conversion] direction=(%.6f,%.6f) reference=(%.6f,%.6f) acceleration=(%.6f,%.6f) first=(%.6f,%.6f) second=(%.6f,%.6f) filtered=(%.6f,%.6f)",
        c.direction[0],c.direction[1],c.referenceHorizon[0],c.referenceHorizon[1],
        c.accelerationHorizon[0],c.accelerationHorizon[1],c.firstPoint[0],c.firstPoint[1],
        c.secondPoint[0],c.secondPoint[1],c.filteredPosition[0],c.filteredPosition[1]);
    }
  }
}
void NativePointerQueryObservation(const CPUState* state,uint32_t site) {
  // Only this caller has a native return site. Ignore unsupported/indirect
  // callers rather than retaining an observation that can never be paired.
  if (site==0x803fb0ec && state->lr==0x80178ec8) PointerQueryEntry(state);
  else if (site==0x80178ec8) PointerQueryReturn(state);
}
const ModernGekkoModDesc* PointerHookDescriptor() {
  static const ModernGekkoModHook hooks[]={
    RECOMP_HOOK(0x803fb0ec,[](CPUState* state) { PointerQueryEntry(state); }),
    RECOMP_HOOK_RETURN(0x803fb0ec,[](CPUState* state) { PointerQueryReturn(state); })};
  static const ModernGekkoModDesc descriptor=[] {
    ModernGekkoModDesc value{};
    value.abi_version=MODERNGEKKO_MOD_ABI_VERSION;
    value.cpu_abi_version=MODERNGEKKO_CPU_ABI_VERSION;
    value.cpu_state_size=sizeof(CPUState);
    const char id[]="RMGE01";
    for (unsigned i=0;i<sizeof(id);++i) value.game_id[i]=id[i];
    value.id="galaxypad.pointer-observer"; value.version="0.1.0";
    value.display_name="GalaxyPad pointer observer";
    value.hooks=hooks; value.num_hooks=2;
    value.on_load=[](const ModernGekkoModHostApi*) { pointerHookProbe={}; };
    return value;
  }();
  return &descriptor;
}
} // namespace
} // namespace galaxypad
