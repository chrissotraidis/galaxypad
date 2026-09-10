// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
#include <optional>

namespace galaxypad {
// CPU-thread-owned policy, no input injection or guest-memory access.
// An epoch must change on scene/host lifecycle transitions, not just pointer mode.
struct DirectTapRequest {
  uint64_t gesture=0, epoch=0, pointerRevision=0, deadline=0;
  uint32_t target=0;
};
struct DirectTapObservation {
  uint64_t epoch=0, pointerRevision=0;
  uint32_t target=0;
  bool contextKnown=false, ready=false, aReleased=false;
};
// Caller must supply a target hit-tested at this request's pointer position and
// observations AFTER guest processing of that pointer revision. Host publication,
// device consumption, a VI count or cached FileSelector hover alone is NOT proof.
// now/deadline use the same monotonic host clock so pause cannot preserve a tap.
class DirectTapQueue {
public:
  bool begin(DirectTapRequest request, uint64_t now) {
    pending_.reset(); // even a malformed replacement must cancel the old tap
    if (!request.gesture || request.gesture<=lastGesture_ || !request.epoch ||
        !request.pointerRevision || !request.target || request.deadline<=now)
      return false;
    lastGesture_=request.gesture;
    pending_=request;
    return true;
  }
  void cancel() { pending_.reset(); }
  bool pending() const { return pending_.has_value(); }
  bool observe(DirectTapObservation observation, uint64_t now) {
    if (!pending_) return false;
    const auto request=*pending_;
    if (now>=request.deadline || !observation.contextKnown ||
        observation.epoch!=request.epoch ||
        observation.pointerRevision>request.pointerRevision) {
      cancel();
      return false;
    }
    // Old target state is neither acceptance nor a reason to reject a new tap.
    if (observation.pointerRevision<request.pointerRevision) return false;
    if (observation.target && observation.target!=request.target) {
      cancel();
      return false;
    }
    if (observation.target!=request.target || !observation.ready ||
        !observation.aReleased) return false;
    cancel();
    return true; // one-shot permission; caller must still preserve ordinary A/B
  }
private:
  uint64_t lastGesture_=0;
  std::optional<DirectTapRequest> pending_;
};
} // namespace galaxypad
