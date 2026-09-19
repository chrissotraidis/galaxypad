// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <cmath>

namespace galaxypad {
// UIKit-independent integration. Angles are radians, time is monotonic seconds.
// Rotation about screen-up steers horizontally; screen-right controls elevation.
class GyroAim {
public:
  enum class Orientation { Portrait, UpsideDown, LandscapeLeft, LandscapeRight };
  void reset() { x_=y_=0.5f; lastSample_=0; }
  void anchor(float x,float y) {
    x_=coordinate(x); y_=coordinate(y);
  }
  void stick(float x,float y,double seconds) {
    if (!std::isfinite(seconds) || seconds<=0 || seconds>.1) return;
    x_=coordinate(x_+axis(x)*seconds*1.2);
    y_=coordinate(y_-axis(y)*seconds*1.2);
  }
  bool sample(double pitch,double yaw,double timestamp,double now,
              float sensitivity,bool invertY) {
    if (!std::isfinite(pitch)||!std::isfinite(yaw)||!std::isfinite(timestamp)||
        !std::isfinite(now)||timestamp<=0 || timestamp>now+.01 || now-timestamp>.25) {
      lastSample_=0; return false;
    }
    if (lastSample_==0) { lastSample_=timestamp; return true; }
    if (timestamp==lastSample_) return true; // polling must not integrate twice
    double dt=timestamp-lastSample_;
    lastSample_=timestamp;
    if (dt<=0 || dt>.1) return true; // resume without integrating a backlog
    const float gain=std::isfinite(sensitivity)?std::clamp(sensitivity,.5f,1.5f):1;
    // One radian traverses the viewport at 1x. Suppress tiny stationary noise.
    auto quiet=[](double rate) { return std::abs(rate)<.012 ? 0.0 : std::clamp(rate,-12.0,12.0); };
    x_=coordinate(x_-quiet(yaw)*dt*gain);
    y_=coordinate(y_-quiet(pitch)*dt*gain*(invertY?-1:1));
    return true;
  }
  static void screenRates(double x,double y,Orientation orientation,double& pitch,double& yaw) {
    switch(orientation) {
      case Orientation::LandscapeLeft: pitch=-y; yaw=x; break;
      case Orientation::LandscapeRight: pitch=y; yaw=-x; break;
      case Orientation::UpsideDown: pitch=-x; yaw=-y; break;
      default: pitch=x; yaw=y; break;
    }
  }
  float x() const { return x_; }
  float y() const { return y_; }
private:
  static float coordinate(double v) { return std::isfinite(v)?std::clamp(v,0.0,1.0):.5; }
  static float axis(float v) {
    if(!std::isfinite(v)) return 0;
    v=std::clamp(v,-1.f,1.f);
    return std::abs(v)<=.15f?0:std::copysign((std::abs(v)-.15f)/.85f,v);
  }
  float x_=.5f,y_=.5f;
  double lastSample_=0;
};
}
