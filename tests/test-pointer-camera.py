#!/usr/bin/env python3
"""Execute actual checkout camera projection and Matrix implementation.

Narrow neutral-motion projection test, not a KPAD inverse or touch calibration.
"""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root / "ref/ModernGekko/vendor/dolphin/Source/Core"
camera = (core / "Core/HW/WiimoteEmu/Camera.cpp").read_text()
header = (core / "Core/HW/WiimoteEmu/Camera.h").read_text()
start = camera.index("std::array<CameraPoint, CameraLogic::NUM_POINTS>\nCameraLogic::GetCameraPoints")
end = camera.index("\nvoid CameraLogic::Update", start)
point = header[header.index("using IRObject"):header.index("// Four bytes")]
names = ["SENSOR_BAR_LED_SEPARATION", "CAMERA_RES_X", "CAMERA_RES_Y",
         "CAMERA_AR", "CAMERA_FOV_X", "CAMERA_FOV_Y", "NUM_POINTS", "MAX_POINT_SIZE"]
constants = []
for name in names:
    matches = re.findall(r"static constexpr [^;\n]+\b" + name + r"\s*=[^;]+;", header)
    assert len(matches) == 1, name
    constants.append(matches[0])
preamble = '''
#include "Common/Matrix.h"
#include "Common/MathUtil.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include "apple/shared/GalaxyPadPointerInverse.h"
#include "apple/shared/GalaxyPadPointerModel.h"
#include "apple/shared/GalaxyPadMenuPointerReadiness.h"
namespace WiimoteEmu {
'''
declaration = "class CameraLogic { public:\n" + "\n".join(constants) + '''
static std::array<CameraPoint,NUM_POINTS> GetCameraPoints(const Common::Matrix44&,Common::Vec2);
};
'''
checks = r'''
} // namespace WiimoteEmu
using namespace Common;
using namespace WiimoteEmu;
auto project(float x,float y,float height,float totalPitch=20) {
  // Neutral swing/tilt/IMU. Same yaw/pitch signs and matrix order as
  // EmulatePoint -> GetTransformation, after the target angle has settled.
  const float yaw=25*float(MathUtil::TAU)/360/2;
  const float pitch=totalPitch*float(MathUtil::TAU)/360/2;
  auto rotation=Matrix33::RotateZ(yaw*x)*Matrix33::RotateX(pitch*y);
  auto transform=Matrix44::FromMatrix33(rotation)*Matrix44::Translate({0,-2,height});
  return CameraLogic::GetCameraPoints(transform,
    {CameraLogic::CAMERA_FOV_X,CameraLogic::CAMERA_FOV_Y});
}
int main() {
  auto center=project(0,0,0);
  fprintf(stderr,"center LEDs=(%u,%u),(%u,%u)\n",center[0].position.x,
    center[0].position.y,center[1].position.x,center[1].position.y);
  assert(center[0].position.x<1024 && center[1].position.x<1024);
  // Float quarter-turn cosine is not exactly zero; CameraLogic truncates,
  // rather than rounds, so the ideal center can become row383 instead of384.
  assert(center[0].position.y==center[1].position.y);
  assert(center[0].position.y==383 || center[0].position.y==384);
  assert(std::abs(int(center[0].position.x)+int(center[1].position.x)-1024)<=2);
  assert(center[2].position.x==0xffff && center[3].position.x==0xffff);
  auto above=project(0,0,.1f), below=project(0,0,-.1f);
  assert(above[0].position.y!=below[0].position.y);
  auto hidden=CameraLogic::GetCameraPoints(Matrix44::Translate({0,1000,0}),
    {CameraLogic::CAMERA_FOV_X,CameraLogic::CAMERA_FOV_Y});
  for (const auto& point:hidden) assert(point.position.x==0xffff);
  for (auto xy: {Vec2{.38f,.64f},Vec2{.61f,.64f},Vec2{.5f,.5f}}) {
    // Mobile PointerUp-PointerDown is 1-2*hostY.
    auto points=project(2*xy.x-1,1-2*xy.y,.1f);
    printf("host=(%.2f,%.2f) LEDs=(%u,%u),(%u,%u)\n",xy.x,xy.y,
      points[0].position.x,points[0].position.y,points[1].position.x,points[1].position.y);
    assert(points[0].position.x<1024 && points[1].position.x<1024);
  }
  puts("Actual camera projection: center, sensor offset, hidden and two-target probes pass; KPAD unmodeled");
  // R578 live regular-point snapshot. WPAD's retail basic/extended parsers
  // invert sensor Y before KPAD normalization; do not invert the host controls.
  auto target=project(2*.38f-1,1-2*.64f,.1f);
  const Vec2 observed[]={{.274414f,-.264648f},{.006836f,-.262695f}};
  for(unsigned i=0;i<2;i++) {
    float x=(2.f*target[i].position.x-1023)/1024;
    float y=(2.f*(767-target[i].position.y)-767)/1024;
    assert(std::abs(x-observed[i].x)<1e-6f && std::abs(y-observed[i].y)<1e-6f);
  }
  puts("R578 fixture: projected LEDs plus WPAD Y inversion match both live KPAD points; tracking/order unmodeled");
  using galaxypad::PointerPoint;
  float totalPitch=20;
  auto forward=[&](PointerPoint host)->std::optional<PointerPoint> {
    return galaxypad::ProjectMenuPointer(host,
      galaxypad::MenuPointerConfiguration{25,totalPitch,.1f,{0,-.2f},2.272727f,true},
      [](const Matrix44& transform){return CameraLogic::GetCameraPoints(transform,
        {CameraLogic::CAMERA_FOV_X,CameraLogic::CAMERA_FOV_Y});});
  };
  for(float pitch: {20.f,22.f,24.f}) {
  totalPitch=pitch;
  unsigned solved=0;
  float worstRejectedBestError=0, bestRejectedBestError=1;
  for(unsigned x=0;x<=20;x++)for(unsigned y=0;y<=20;y++) {
    PointerPoint desired{x/20.f,y/20.f};
    unsigned evaluations=0;
    float bestError=1;
    auto inverse=galaxypad::InvertPointer(desired,[&](PointerPoint p){
      ++evaluations;auto value=forward(p);
      if(value) bestError=std::min(bestError,std::max(std::abs(value->x-desired.x),
                                                   std::abs(value->y-desired.y)));
      return value;
    });
    assert(evaluations<=75);
    if(inverse) {
      auto value=forward(*inverse);
      assert(value && std::abs(value->x-desired.x)<=galaxypad::PointerInverseTolerance &&
        std::abs(value->y-desired.y)<=galaxypad::PointerInverseTolerance);
      ++solved;
    } else {
      worstRejectedBestError=std::max(worstRejectedBestError,bestError);
      bestRejectedBestError=std::min(bestRejectedBestError,bestError);
    }
  }
  // Important UI targets must solve, not merely produce safe rejection.
  for(PointerPoint desired: {PointerPoint{.38f,.64f},{.61f,.64f},{.68f,.92f},
                             {.5f,.999f},{.02f,.5f},{.98f,.5f}}) {
    auto inverse=galaxypad::InvertPointer(desired,forward);
    if(pitch==20 && desired.y>.99f) { assert(!inverse); continue; }
    assert(inverse);
    printf("pitch%.0f target(%.2f,%.2f) input(%.6f,%.6f)\n",pitch,desired.x,desired.y,
      inverse->x,inverse->y);
  }
  assert(solved==(pitch==20 ? 420u : 441u));
  assert(!galaxypad::InvertPointer(PointerPoint{-1,0},forward));
  assert(!galaxypad::InvertPointer(PointerPoint{NAN,0},forward));
  assert(!galaxypad::InvertPointer(PointerPoint{.5f,1.1f},forward));
  assert(!galaxypad::InvertPointer(PointerPoint{.5f,.5f},[](PointerPoint)
    ->std::optional<PointerPoint>{return std::nullopt;}));
  assert(!galaxypad::InvertPointer(PointerPoint{.7f,.2f},[](PointerPoint){
    return std::optional(PointerPoint{.5f,.5f});
  }));
  assert(!galaxypad::InvertPointer(PointerPoint{.7f,.2f},[](PointerPoint){
    return std::optional(PointerPoint{NAN,0});
  }));
  printf("Bounded inverse pitch%.0f: %u/441 viewport targets solve within %.4f; others reject; key menu targets pass\n",pitch,solved,galaxypad::PointerInverseTolerance);
  if(solved<441) printf("Rejected targets best sampled error range: %.7f .. %.7f\n",
    bestRejectedBestError,worstRejectedBestError);
  }
  totalPitch=22;
  struct LiveFixture { PointerPoint input,screen; };
  for(auto fixture: {LiveFixture{{.411593f,.685748f},{315.896f,291.972f}},
      {{.5f,.985020f},{416,455.818f}},{{.142481f,.568570f},{17.164f,228.026f}},
      {{.857519f,.568570f},{814.836f,228.026f}}}) {
    auto value=forward(fixture.input);
    assert(value && std::abs(value->x*832-fixture.screen.x)<.002f &&
      std::abs(value->y*456-fixture.screen.y)<.002f);
  }
  galaxypad::MenuPointerConfiguration config{25,22,.1f,{0,-.2f},2.272727f};
  unsigned cameraCalls=0;
  auto camera=[&](const Matrix44& transform){++cameraCalls;
    return CameraLogic::GetCameraPoints(transform,
      {CameraLogic::CAMERA_FOV_X,CameraLogic::CAMERA_FOV_Y});};
  assert(!galaxypad::ProjectMenuPointer(PointerPoint{.5f,.5f},config,camera));
  assert(cameraCalls==0); // Unknown orientation fails before projection.
  config.neutralOrientationVerified=true;
  for(float invalid: {0.f,-1.f,NAN,INFINITY}) {
    config.scale=invalid;
    assert(!galaxypad::ProjectMenuPointer(PointerPoint{.5f,.5f},config,camera));
  }
  config.scale=2.272727f;
  for(float invalid: {0.f,180.f,NAN,INFINITY}) {
    config.totalPitch=invalid;
    assert(!galaxypad::ProjectMenuPointer(PointerPoint{.5f,.5f},config,camera));
  }
  config.totalPitch=22;
  assert(!galaxypad::ProjectMenuPointer(PointerPoint{.5f,.5f},config,
    [](const Matrix44&){return std::array<CameraPoint,2>{};}));
  assert(!galaxypad::ProjectMenuPointer(PointerPoint{.5f,.5f},config,
    [](const Matrix44&){return std::array{CameraPoint{{512,384},1},CameraPoint{{512,384},1}};}));
  puts("Shared menu model: four live fixtures within .002 logical pixels; unknown/invalid configuration and missing/degenerate LEDs reject");
  galaxypad::PointerContext context{0x8091f3d8,5};
  galaxypad::ActorPointerState actor{0x80010000,0x806a0114,0};
  galaxypad::PointerCalibration calibration{0,-.2f,2.272727f,.03f,.5f,0};
  galaxypad::PointerConversionInputs conversion{};
  conversion.referenceHorizon={1,0};conversion.accelerationHorizon={0,-1};
  auto ready=[&]{return galaxypad::MenuPointerReadiness(true,context,actor,calibration,conversion);};
  assert(ready() && ready()->totalPitch==22 && ready()->neutralOrientationVerified);
  assert(!galaxypad::MenuPointerReadiness(false,context,actor,calibration,conversion));
  assert(!galaxypad::MenuPointerReadiness(true,std::nullopt,actor,calibration,conversion));
  assert(!galaxypad::MenuPointerReadiness(true,context,std::nullopt,calibration,conversion));
  assert(!galaxypad::MenuPointerReadiness(true,context,actor,std::nullopt,conversion));
  assert(!galaxypad::MenuPointerReadiness(true,context,actor,calibration,std::nullopt));
  context.mode=4;assert(!ready());context.mode=5;
  actor.pending=0x806a0118;assert(!ready());actor.pending=0;
  actor.current=0x806a0118;assert(!ready());actor.current=0x806a0114;
  actor.current=0x806a0128;assert(ready()); // R552/R585 stable file detail.
  actor.pending=0x806a0110;assert(!ready());actor.pending=0;
  actor.current=0x806a0110;assert(!ready()); // Back animation, not stable detail.
  actor.current=0x806a0114;
  calibration.filterMode=1;assert(!ready());calibration.filterMode=0;
  calibration.centerY=.2f;assert(!ready());calibration.centerY=-.2f;
  calibration.scale=NAN;assert(!ready());calibration.scale=2.272727f;
  conversion.accelerationHorizon={.01f,-1};assert(!ready());
  conversion.accelerationHorizon={0,-1};
  conversion.referenceHorizon={0,1};assert(!ready());
  conversion.referenceHorizon={1,0};assert(ready());
  puts("Menu mapping readiness: profile, context, pending transition, calibration and neutral horizons fail closed");
}
'''
with tempfile.TemporaryDirectory(prefix="galaxypad-camera-") as temp:
    path = Path(temp)
    (path / "probe.cpp").write_text(preamble + point + declaration + camera[start:end] + checks)
    subprocess.run(["xcrun", "clang++", "-std=c++23", "-fsanitize=address,undefined",
                    "-I", str(core), "-I", str(root), str(path / "probe.cpp"), str(core / "Common/Matrix.cpp"),
                    "-o", str(path / "probe")], check=True)
    subprocess.run([str(path / "probe")], check=True)
