#!/usr/bin/env python3
"""Fit IR yaw/pitch/sensor height so the modeled settled cursor lands under the finger.

Uses the checkout's actual Dolphin camera projection and GalaxyPad's shared pointer
model (neutral orientation, retail KPAD calibration). Offline only.
"""
from pathlib import Path
import argparse, re, subprocess, tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--core', type=Path, help='Pinned Source/Core directory')
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
core = a.core or root/'ref/ModernGekko/vendor/dolphin/Source/Core'
camera = (core/'Core/HW/WiimoteEmu/Camera.cpp').read_text()
header = (core/'Core/HW/WiimoteEmu/Camera.h').read_text()
start = camera.index("std::array<CameraPoint, CameraLogic::NUM_POINTS>\nCameraLogic::GetCameraPoints")
end = camera.index("\nvoid CameraLogic::Update", start)
point = header[header.index("using IRObject"):header.index("// Four bytes")]
names = ["SENSOR_BAR_LED_SEPARATION", "CAMERA_RES_X", "CAMERA_RES_Y", "CAMERA_AR", "CAMERA_FOV_X",
         "CAMERA_FOV_Y", "NUM_POINTS", "MAX_POINT_SIZE"]
constants = [re.findall(r"static constexpr [^;\n]+\b" + n + r"\s*=[^;]+;", header)[0] for n in names]
src = '''
#include "Common/Matrix.h"
#include "Common/MathUtil.h"
#include <algorithm>
#include <cstdio>
#include <cmath>
#include "apple/shared/GalaxyPadPointerInverse.h"
#include "apple/shared/GalaxyPadPointerModel.h"
namespace WiimoteEmu {
''' + point + "class CameraLogic { public:\n" + "\n".join(constants) + '''
static std::array<CameraPoint,NUM_POINTS> GetCameraPoints(const Common::Matrix44&,Common::Vec2);
};
''' + camera[start:end] + r'''
} // namespace WiimoteEmu
using namespace WiimoteEmu; using galaxypad::PointerPoint;
struct Fit { float worst, mean; int missing; };
Fit score(float yaw, float pitch, float height, bool print=false) {
  galaxypad::MenuPointerConfiguration c{yaw,pitch,height,{0,-.2f},2.272727f,true};
  auto cam=[](const Common::Matrix44& t){return CameraLogic::GetCameraPoints(t,{CameraLogic::CAMERA_FOV_X,CameraLogic::CAMERA_FOV_Y});};
  float worst=0,sum=0; int n=0,missing=0;
  for(int i=1;i<=19;i++) for(int j=1;j<=19;j++) {
    PointerPoint f{i/20.f,j/20.f};
    auto v=galaxypad::ProjectMenuPointer(f,c,cam);
    if(!v){missing++;continue;}
    // Error in logical points on the phone's 16:9 gameplay viewport (832x468).
    float e=std::hypot((v->x-f.x)*832,(v->y-f.y)*468);
    worst=std::max(worst,e); sum+=e; n++;
    if(print && (i%6==1) && (j%6==1)) printf("  finger(%.2f,%.2f) -> cursor(%.3f,%.3f) error %.1f pt\n",f.x,f.y,v->x,v->y,e);
  }
  return {worst,n?sum/n:1e9f,missing};
}
int main(){
  auto base=score(25,20,.1f,true);
  printf("CURRENT yaw25 pitch20 height0.10: worst %.1f pt, mean %.1f pt, off-screen %d/361\n",base.worst,base.mean,base.missing);
  float by=0,bp=0,bh=0; Fit best{1e9,1e9,999};
  for(float yaw=10;yaw<=40;yaw+=.25f) for(float pitch=8;pitch<=36;pitch+=.25f) for(float h=-.3f;h<=.4f;h+=.01f){
    auto s=score(yaw,pitch,h); if(s.missing) continue;
    if(s.mean<best.mean){best=s;by=yaw;bp=pitch;bh=h;}
  }
  printf("BEST yaw%.2f pitch%.2f height%.2f: worst %.1f pt, mean %.1f pt\n",by,bp,bh,best.worst,best.mean);
  score(by,bp,bh,true);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-touch-fit-') as t:
    t = Path(t); (t/'fit.cpp').write_text(src)
    subprocess.run(['xcrun', 'clang++', '-std=c++23', '-O2', '-I', str(core), '-I', str(root), str(t/'fit.cpp'),
                    str(core/'Common/Matrix.cpp'), '-o', str(t/'fit')], check=True)
    subprocess.run([str(t/'fit')], check=True)
