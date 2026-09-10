// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace galaxypad {
// Diagnostic only: each instance belongs to one serialized input boundary.
// No clocks or output when disabled; bounded change records, never per-frame I/O.
class MovementTrace {
public:
  explicit MovementTrace(const char* stage) : stage_(stage) {
    const char* value=std::getenv("GALAXYPAD_MOVEMENT_TRACE");
    enabled_=value && std::strcmp(value,"1")==0;
  }
  void record(float x,float y) {
    if (!enabled_ || records_>=128) return;
    ++polls_;
    if (x==x_ && y==y_) return;
    x_=x; y_=y; ++records_;
    const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
    std::fprintf(stderr,"GalaxyPadMovement stage=%s ns=%lld poll=%llu x=%.6f y=%.6f\n",
        stage_,static_cast<long long>(ns),polls_,x,y);
  }
private:
  const char* stage_;
  bool enabled_=false;
  unsigned records_=0;
  unsigned long long polls_=0;
  float x_=0,y_=0;
};
}
