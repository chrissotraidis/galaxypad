#include "MetalEfbBatch.h"
#include "EfbBatchProbe.h"
#include <cassert>
namespace galaxypad::efb_direct_batch {
unsigned endings=0;
void EndMetalBatch() {++endings;}
bool HasMetalBatch() {return false;}
}
int main() {
  namespace b=galaxypad::efb_direct_batch;
  assert(!galaxypad::efb_batch_probe::Enabled());
  {b::RefreshScope r;b::PopulateScope p;assert(!b::Eligible());}
  assert(b::endings==0);
  b::enabled=true;
  {b::PopulateScope demand;assert(!b::Eligible());}
  {b::RefreshScope refresh;
    assert(!b::Eligible());
    {b::PopulateScope direct;assert(b::Eligible());}
    assert(!b::Eligible());
    {b::PopulateScope intermediate;intermediate.setIntermediate(true);assert(!b::Eligible());}
    {b::PopulateScope direct;assert(b::Eligible());}}
  assert(b::endings==1 && !b::Eligible());
  assert(!galaxypad::efb_batch_probe::Enabled()); // Independent runtime switches.
}
