// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadControllerSlots.h"
#include "../apple/shared/GalaxyPadControllerInput.h"
#include <cassert>
#include <cstdio>
#include <limits>
int main() {
  GalaxyPadControllerSlots slots;
  auto initial=slots.Reconcile({0,11,11,22});
  assert(initial.assigned.size()==1 && slots.InstanceAt(0)==11);
  assert(slots.Reconcile({22,11}).assigned.empty()); // arrival ordering cannot steal P1
  auto handoff=slots.Reconcile({22});
  assert(handoff.removed.size()==1 && handoff.assigned.size()==1);
  assert(slots.InstanceAt(0)==22 && slots.SlotFor(11)==-1);
  assert(slots.Reconcile({}).removed.size()==1 && slots.InstanceAt(0)==0);

  using namespace galaxypad;
  ControllerMapping permutation;
  unsigned permutations=0;
  do {
    assert(permutation.valid() && permutation.apply(31)==(A|B|Spin|C|Z));
    for (unsigned game=0;game<5;++game) for (unsigned button=0;button<5;++button) {
      auto swapped=permutation.assigning(game,button);
      assert(swapped.valid() && swapped.physical[game]==button);
    }
    ++permutations;
  } while (std::next_permutation(permutation.physical.begin(),permutation.physical.end()));
  assert(permutations==120);
  ControllerMapping invalidMap; invalidMap.physical[0]=99;
  assert(!invalidMap.valid() && invalidMap.apply(1)==A);
  ControllerInput input;
  ControllerSnapshot pad;
  pad.a=true;
  assert(input.update(pad,1.f/60).buttons==0); // connected while held
  pad={}; input.update(pad,1.f/60);
  pad.a=pad.b=pad.x=pad.y=pad.leftTrigger=pad.menu=pad.options=true;
  auto held=input.update(pad,1.f/60);
  assert(held.buttons==(A|B|Spin|C|Z|Plus|Minus));
  input.reset();
  assert(input.update(pad,1.f/60).buttons==0);
  pad={}; input.update(pad,1.f/60);
  pad.rightX=1;
  auto aim=input.update(pad,1.f/60);
  assert(aim.pointerVisible && aim.pointerX>0.5f && aim.pointerY==0.5f);
  pad.rightShoulder=true;
  auto grab=input.update(pad,1.f/60);
  assert(grab.buttons==A && grab.pointerVisible && grab.pointerX>aim.pointerX);
  pad.rightTrigger=true;
  auto chord=input.update(pad,1.f/60);
  assert(chord.buttons==(A|B) && chord.pointerX>grab.pointerX);
  pad.rightShoulder=false;
  assert(input.update(pad,0).buttons==B); // release A without dropping B or aim
  pad.rightTrigger=false; pad.y=true;
  assert(input.update(pad,0).buttons==C); // camera remains reachable
  pad.y=false;
  aim=input.update(pad,0);
  pad.leftShoulder=true; pad.rightY=1;
  auto tilt=input.update(pad,1.f/60);
  assert(tilt.tiltX==1 && tilt.tiltY==1 && !tilt.pointerVisible);
  assert(tilt.pointerX==aim.pointerX);
  pad={};
  auto release=input.update(pad,1.f/60);
  assert(release.buttons==0 && release.tiltX==0 && release.tiltY==0);
  pad.recenter=true;
  auto centered=input.update(pad,1.f/60);
  assert(centered.pointerX==0.5f && centered.pointerY==0.5f);
  pad={}; pad.moveX=std::numeric_limits<float>::quiet_NaN(); pad.rightX=1;
  auto invalid=input.update(pad,std::numeric_limits<float>::infinity());
  assert(invalid.moveX==0 && invalid.pointerX==0.5f);
  auto bounded=input.update(pad,10);
  assert(bounded.pointerX<=0.563f);
  input.reset(); pad.moveX=1;
  assert(!input.update(pad,1.f/60).connected); // neutral gate covers axes too
  pad={}; input.update(pad,0);
  assert(input.update(pad,0).connected);
  input.setMapping(ControllerMapping{}.assigning(0,2));
  pad.a=true;
  assert(input.update(pad,0).buttons==0); // remapping requires release
  pad={}; input.update(pad,0);
  pad.a=true;
  assert(input.update(pad,0).buttons==Spin);
  puts("Galaxy controller ownership, mapping, pointer, tilt and reset tests pass");
}
