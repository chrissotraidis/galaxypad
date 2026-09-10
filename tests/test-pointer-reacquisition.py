#!/usr/bin/env python3
"""Compile the checkout's actual EmulatePoint body with narrow dependency doubles.

Proves its visibility/branch contract, not final IR projection or gameplay timing.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "ref/ModernGekko/vendor/dolphin/Source/Core/Core/HW/WiimoteEmu/Dynamics.cpp").read_text()
start = source.index("void EmulatePoint(")
end = source.index("\nvoid ApproachAngleWithAccel(", start)
body = source[start:end]
preamble = r'''
#include <cassert>
#include <cmath>
#include <cstdio>
namespace Common { struct Vec3 {
  float x=0,y=0,z=0;
  Vec3()=default; Vec3(float a,float b,float c):x(a),y(b),z(c) {}
}; }
struct MotionState { Common::Vec3 position,velocity,acceleration,angle,angular_velocity; };
namespace MathUtil { constexpr double TAU=6.283185307179586; }
namespace Config { constexpr int SYSCONF_SENSOR_BAR_POSITION=0; bool top=true; bool Get(int) {return top;} }
namespace ControllerEmu {
struct InputOverrideFunction {};
struct Cursor {
  struct State { float x=.6f,y=-.4f; bool visible=true; bool IsVisible() const {return visible;} } state;
  State GetState(bool,const InputOverrideFunction&) {return state;}
  float GetVerticalOffset() const {return .1f;}
  float GetTotalYaw() const {return .5f;}
  float GetTotalPitch() const {return .4f;}
}; }
int smooth_calls=0;
void ApproachAngleWithAccel(MotionState*, const Common::Vec3&, float, float) {++smooth_calls;}
'''
checks = r'''
int main() {
  MotionState state;
  ControllerEmu::Cursor cursor;
  cursor.state.visible=false;
  EmulatePoint(&state,&cursor,{},.005f);
  assert(state.position.y==-1000 && smooth_calls==0);
  cursor.state.visible=true;
  EmulatePoint(&state,&cursor,{},.005f);
  assert(smooth_calls==0); // hidden -> visible must jump, not smooth from zero
  assert(state.position.y==2 && state.position.z==-.1f);
  assert(std::abs(state.angle.x-.08f)<1e-6 && std::abs(state.angle.z+.15f)<1e-6);
  assert(state.angular_velocity.x==0 && state.angular_velocity.z==0);
  EmulatePoint(&state,&cursor,{},.005f);
  assert(smooth_calls==1); // normal visible motion keeps its existing smoothing
  cursor.state.visible=false; EmulatePoint(&state,&cursor,{},.005f);
  cursor.state.visible=true; Config::top=false;
  EmulatePoint(&state,&cursor,{},.005f);
  assert(smooth_calls==1 && state.position.z==.1f);
  puts("Actual EmulatePoint body: reacquisition, visible smoothing and sensor offset pass");
}
'''
with tempfile.TemporaryDirectory(prefix="galaxypad-pointer-") as directory:
    directory = Path(directory)
    (directory / "test.cpp").write_text(preamble + body + checks)
    subprocess.run(["xcrun", "clang++", "-std=c++23", "-fsanitize=address,undefined",
                    str(directory / "test.cpp"), "-o", str(directory / "test")], check=True)
    subprocess.run([str(directory / "test")], check=True)
