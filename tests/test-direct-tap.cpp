#include "../apple/shared/GalaxyPadDirectTap.h"
#include <cassert>
#include <iostream>
using namespace galaxypad;
int main() {
  DirectTapQueue q;
  uint64_t gesture=0;
  auto begin=[&] { assert(q.begin({++gesture,7,20,100,0x81144cc8},10)); };
  const DirectTapObservation good{7,20,0x81144cc8,true,true,true};
  begin();
  auto old=good; old.pointerRevision=19; old.target=0x81192d08;
  assert(!q.observe(old,11) && q.pending()); // stale hover never selects
  assert(q.observe(good,12) && !q.pending());
  assert(!q.observe(good,13)); // repeated observation cannot repeat A
  assert(!q.begin({gesture,7,20,100,0x81144cc8},14)); // replayed gesture
  begin();
  auto absent=good; absent.target=0;
  assert(!q.observe(absent,11) && q.pending());
  auto disabled=good; disabled.ready=false;
  assert(!q.observe(disabled,12) && q.pending());
  auto held=good; held.aReleased=false;
  assert(!q.observe(held,13) && q.pending()); // cannot merge into held A
  assert(q.observe(good,14));
  for (unsigned kind=0;kind<4;++kind) {
    begin(); auto bad=good;
    if (kind==0) bad.epoch=8;
    if (kind==1) bad.contextKnown=false;
    if (kind==2) bad.pointerRevision=21;
    if (kind==3) bad.target=0x81192d08;
    assert(!q.observe(bad,11) && !q.pending());
    assert(!q.observe(good,12)); // cannot revive after scene/cursor changes
  }
  begin(); assert(!q.observe(good,100) && !q.pending());
  begin(); q.cancel(); assert(!q.observe(good,11)); // finger/menu/lifecycle
  begin(); assert(!q.begin({},11) && !q.pending());
  begin();
  assert(q.begin({++gesture,7,21,100,0x81192d08},11));
  assert(!q.observe(good,12) && q.pending());
  auto replacement=good; replacement.pointerRevision=21; replacement.target=0x81192d08;
  assert(q.observe(replacement,13));
  std::cout << "Direct tap: freshness, epoch, target, expiry, cancellation and one-shot pass\n";
}
