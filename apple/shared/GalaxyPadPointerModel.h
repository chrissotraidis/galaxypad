// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "GalaxyPadPointerInverse.h"
#include "Common/Matrix.h"
#include "Common/MathUtil.h"

namespace galaxypad {
struct MenuPointerConfiguration {
  float totalYaw, totalPitch, sensorHeight;
  PointerPoint center;
  float scale;
  // Caller must verify neutral motion and retail reference/acceleration horizons.
  // This model must not silently stand in for tilted/shaken/unknown state.
  bool neutralOrientationVerified=false;
};

// Camera callback receives the settled transformation and returns actual camera
// points using the active FOV. No guest reads, input mutation or tracking state.
template<class Camera>
std::optional<PointerPoint> ProjectMenuPointer(PointerPoint host,
    const MenuPointerConfiguration& config, Camera camera) {
  if (!config.neutralOrientationVerified || !std::isfinite(host.x) ||
      !std::isfinite(host.y) || host.x<0 || host.x>1 || host.y<0 || host.y>1 ||
      !std::isfinite(config.totalYaw) || !std::isfinite(config.totalPitch) ||
      !std::isfinite(config.sensorHeight) || !std::isfinite(config.center.x) ||
      !std::isfinite(config.center.y) || !std::isfinite(config.scale) ||
      config.totalYaw<=0 || config.totalYaw>=180 || config.totalPitch<=0 ||
      config.totalPitch>=180 || config.scale<=0) return std::nullopt;
  using namespace Common;
  const float yaw=config.totalYaw*float(MathUtil::TAU)/720;
  const float pitch=config.totalPitch*float(MathUtil::TAU)/720;
  auto rotation=Matrix33::RotateZ(yaw*(2*host.x-1))*Matrix33::RotateX(pitch*(1-2*host.y));
  auto points=camera(Matrix44::FromMatrix33(rotation)*
                     Matrix44::Translate({0,-2,config.sensorHeight}));
  Vec2 p[2];
  for(unsigned i=0;i<2;++i) {
    if(points[i].position.x>=1024 || points[i].position.y>=768) return std::nullopt;
    p[i]={(2.f*points[i].position.x-1023)/1024,
          (767-2.f*points[i].position.y)/1024};
  }
  if(p[0].x>p[1].x) std::swap(p[0],p[1]);
  auto separation=p[1]-p[0];
  if(separation.LengthSquared()<1e-8f) return std::nullopt;
  auto direction=separation.Normalized(),midpoint=(p[1]+p[0])*.5f;
  float dot=direction.x,cross=-direction.y;
  float x=(config.center.x-(dot*midpoint.x-cross*midpoint.y))*config.scale;
  float y=(config.center.y-(cross*midpoint.x+dot*midpoint.y))*config.scale;
  if(!std::isfinite(x) || !std::isfinite(y)) return std::nullopt;
  return PointerPoint{(x+1)*.5f,(y+1)*.5f};
}
} // namespace galaxypad
