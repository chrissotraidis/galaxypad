#!/usr/bin/env python3
"""Read-only neutral camera prototype. No input injection or runtime changes.

Usage: python3 experiments/pointer/neutral-gameplay-probe.py X Y [PITCH]
Prints forward guest pixels and inverse rotation input for a desired viewport
point. Uses the checkout's actual Dolphin camera and matrix implementations.
"""
from pathlib import Path
import re
import json
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
core = root / "ref/ModernGekko/vendor/dolphin/Source/Core"
camera = (core / "Core/HW/WiimoteEmu/Camera.cpp").read_text()
header = (core / "Core/HW/WiimoteEmu/Camera.h").read_text()
start = camera.index("std::array<CameraPoint, CameraLogic::NUM_POINTS>\nCameraLogic::GetCameraPoints")
end = camera.index("\nvoid CameraLogic::Update", start)
point = header[header.index("using IRObject"):header.index("// Four bytes")]
constants = []
for name in ["SENSOR_BAR_LED_SEPARATION", "CAMERA_RES_X", "CAMERA_RES_Y",
             "CAMERA_AR", "CAMERA_FOV_X", "CAMERA_FOV_Y", "NUM_POINTS", "MAX_POINT_SIZE"]:
    matches = re.findall(r"static constexpr [^;\n]+\b" + name + r"\s*=[^;]+;", header)
    assert len(matches) == 1, name
    constants.append(matches[0])
source = '''
#include "Common/Matrix.h"
#include "Common/MathUtil.h"
#include "apple/shared/GalaxyPadPointerModel.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
namespace WiimoteEmu {
''' + point + "class CameraLogic { public:\n" + "\n".join(constants) + '''
static std::array<CameraPoint,NUM_POINTS> GetCameraPoints(const Common::Matrix44&,Common::Vec2);
};
''' + camera[start:end] + '''
}
int main(int argc,char**argv) {
  if(argc<3 || argc>4) return 2;
  galaxypad::PointerPoint desired{float(std::atof(argv[1])),float(std::atof(argv[2]))};
  float pitch=argc==4 ? std::atof(argv[3]) : 20;
  auto forward=[&](galaxypad::PointerPoint input) {
    using WiimoteEmu::CameraLogic;
    return galaxypad::ProjectMenuPointer(input,
      galaxypad::MenuPointerConfiguration{25,pitch,.1f,{0,-.2f},2.272727f,true},
      [](const Common::Matrix44& transform) {return CameraLogic::GetCameraPoints(
        transform,{CameraLogic::CAMERA_FOV_X,CameraLogic::CAMERA_FOV_Y});});
  };
  auto projected=forward(desired);
  if(projected) printf("forward input=(%.6f,%.6f) guest=(%.6f,%.6f) normalized=(%.6f,%.6f)\\n",
    desired.x,desired.y,projected->x*832,projected->y*456,projected->x,projected->y);
  auto inverse=galaxypad::InvertPointer(desired,forward);
  if(inverse) {
    auto result=forward(*inverse);
    printf("inverse desired=(%.6f,%.6f) input=(%.6f,%.6f) guest=(%.6f,%.6f)\\n",
      desired.x,desired.y,inverse->x,inverse->y,result->x*832,result->y*456);
  } else puts("inverse rejected");
}
'''
with tempfile.TemporaryDirectory(prefix="galaxypad-gameplay-probe-") as temporary:
    path = Path(temporary)
    (path / "probe.cpp").write_text(source)
    subprocess.run(["xcrun", "clang++", "-std=c++23", "-fsanitize=address,undefined",
                    "-I", str(core), "-I", str(root), str(path / "probe.cpp"),
                    str(core / "Common/Matrix.cpp"), "-o", str(path / "probe")], check=True)
    if sys.argv[1:] == ["--fixtures"]:
        fixtures = json.loads((Path(__file__).with_name("observatory-neutral.json")).read_text())
        for sample in fixtures["samples"]:
            output = subprocess.check_output([str(path / "probe"),
                *map(str, sample["finger"]), str(fixtures["pitch"])], text=True)
            match = re.search(r"guest=\(([-\d.]+),([-\d.]+)\)", output)
            assert match, output
            projected = list(map(float, match.groups()))
            clamped = [min(max(value, 0), dimension)
                       for value, dimension in zip(projected, fixtures["dimensions"])]
            error = max(abs(a-b) for a,b in zip(clamped, sample["current"]))
            assert error <= sample["tolerancePixels"], (sample, projected, error)
            print(f"sample {sample['sample']}: clamped model {clamped}; observed {sample['current']}; max error {error:.6f}px")
    else:
        subprocess.run([str(path / "probe"), *sys.argv[1:]], check=True)
