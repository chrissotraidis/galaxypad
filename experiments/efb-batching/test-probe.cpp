#include "EfbBatchProbe.h"
#include <cassert>
using namespace galaxypad::efb_batch_probe;
int main() {
  {RefreshScope refresh;PopulateScope p;Copy(1,2,3);}
  assert(recorder.totals[Refreshes]==0);
  enabled=true;
  {RefreshScope refresh;
    {PopulateScope p;Copy(1,2,3);}
    {PopulateScope p;Copy(1,2,3);}}
  {RefreshScope refresh;
    {PopulateScope p;p.setIntermediate(true);OtherWork();Copy(1,2,3);}
    {PopulateScope p;p.setIntermediate(true);OtherWork();Copy(1,2,3);}}
  {PopulateScope p;Copy(1,2,3);}
  for(unsigned i=0;i<62;++i) {RefreshScope refresh;}
  assert(publication.load()==0);
  for(unsigned i=0;i<62;++i) {RefreshScope refresh;PopulateScope p;Copy(1,2,3);}
  assert(publication.load()==2);
  auto s=Read();assert(s);
  assert((*s)[Refreshes]==126 && (*s)[ActiveRefreshes]==64);
  assert((*s)[RefreshCopies]==66 && (*s)[DemandCopies]==1);
  assert((*s)[DirectCopies]==65 && (*s)[IntermediateCopies]==2);
  assert((*s)[BlitEncoders]==67 && (*s)[ContiguousPairs]==1 && (*s)[SameResourcePairs]==1);
  assert((*s)[MultiCopyRefreshes]==2 && (*s)[MaximumCopies]==2 && (*s)[MaximumRun]==2);
  for(unsigned i=0;i<1000000;++i) {RefreshScope refresh;}
  assert(recorder.totals[Refreshes]==1000126);
  assert(publication.load()==2); // No repeated publication at active count64.
  assert(Read()->at(Refreshes)==126); // Idle snapshots intentionally remain stale.
  for(unsigned i=0;i<64;++i) {RefreshScope refresh;PopulateScope p;Copy(1,2,3);}
  assert(publication.load()==4);
  assert(Read()->at(Refreshes)==1000190 && Read()->at(ActiveRefreshes)==128);
}
