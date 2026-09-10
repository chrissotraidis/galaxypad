#pragma once
#include "completion-flight-recorder.h"
#include "completion-flight-options.h"

namespace galaxypad {
// Runtime configures before boot and exports only after both workers join.
inline CompletionFlightRecorder completion_recorder;
inline void ObserveCompletion(void*, bool before) noexcept {
  completion_recorder.GraphicsBoundary(before);
}
} // namespace galaxypad
