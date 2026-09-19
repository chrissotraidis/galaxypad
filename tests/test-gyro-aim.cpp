// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadGyroAim.h"
#include <cassert>
#include <limits>
#include <cstdio>
using galaxypad::GyroAim;
int main() {
  GyroAim aim;
  assert(aim.sample(0,0,1,1,1,false));
  assert(aim.sample(1,-1,1.05,1.05,1,false));
  assert(std::abs(aim.x()-.55)<1e-6 && std::abs(aim.y()-.45)<1e-6);
  aim.sample(1,-1,1.05,1.05,1,false);
  assert(std::abs(aim.x()-.55)<1e-6); // duplicate sensor polling
  assert(!aim.sample(1,-1,1.05,1.4,1,false));
  float x=aim.x();
  aim.sample(1,-1,1.41,1.41,1,false);
  assert(aim.x()==x); // stale recovery cannot integrate the missing interval
  aim.reset();aim.sample(0,0,2,2,1,false);
  aim.sample(1,0,2.05,2.05,1,true);
  assert(std::abs(aim.y()-.55)<1e-6);
  aim.anchor(.2,.8);aim.stick(1,1,.05);
  assert(std::abs(aim.x()-.26)<1e-6 && std::abs(aim.y()-.74)<1e-6);
  aim.stick(1,1,20);assert(std::abs(aim.x()-.26)<1e-6);
  aim.anchor(20,-20);assert(aim.x()==1 && aim.y()==0);
  aim.reset();assert(aim.x()==.5 && aim.y()==.5);
  double p,y;
  GyroAim::screenRates(1,2,GyroAim::Orientation::Portrait,p,y);assert(p==1 && y==2);
  GyroAim::screenRates(1,2,GyroAim::Orientation::LandscapeLeft,p,y);assert(p==-2 && y==1);
  GyroAim::screenRates(1,2,GyroAim::Orientation::LandscapeRight,p,y);assert(p==2 && y==-1);
  GyroAim::screenRates(1,2,GyroAim::Orientation::UpsideDown,p,y);assert(p==-1 && y==-2);
  assert(!aim.sample(NAN,0,3,3,1,false));
  assert(!aim.sample(0,0,4,3,1,false));
  assert(!aim.sample(0,0,0,3,1,false));
  aim.sample(0,0,4,4,1,false);aim.sample(.001,.001,4.05,4.05,1,false);
  assert(aim.x()==.5 && aim.y()==.5);
  aim.reset();aim.sample(0,0,5,5,.5,false);
  aim.sample(1,-1,5.05,5.05,.5,false);
  assert(std::abs(aim.x()-.525)<1e-6 && std::abs(aim.y()-.475)<1e-6);
  aim.reset();aim.sample(0,0,6,6,1.5,false);
  aim.sample(1,-1,6.05,6.05,1.5,false);
  assert(std::abs(aim.x()-.575)<1e-6 && std::abs(aim.y()-.425)<1e-6);
  GyroAim fast,slow;
  fast.sample(0,0,10,10,1,false);slow.sample(0,0,10,10,1,false);
  for(int i=1;i<=60;++i) fast.sample(.1,-.1,10+i/60.,10+i/60.,1,false);
  for(int i=1;i<=30;++i) slow.sample(.1,-.1,10+i/30.,10+i/30.,1,false);
  assert(std::abs(fast.x()-slow.x())<1e-5 && std::abs(fast.y()-slow.y())<1e-5);
  puts("Gyro aim: orientation, timing, duplicates, stale data, recenter, sensitivity and stick integration pass");
}
