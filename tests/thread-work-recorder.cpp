#define GALAXYPAD_PRIVATE_THREAD_WORK 1
#include "../patches/experiments/thread-work-recorder.h"
#include <cassert>
#include <fstream>
#include <iterator>
#include <thread>
using R = galaxypad::ThreadWorkRecorder<3>;
static int calls;
static bool fail;
static bool zero_counters;
static std::uint64_t value = 100;
static int read_counts(unsigned kind, void* out, std::size_t bytes) {
  ++calls;
  assert(kind == 4 && bytes == 2*sizeof(R::Counts));
  auto* counts = static_cast<R::Counts*>(out);
  counts[0] = {value,value+1,value+2,value+3};
  counts[1] = {value+4,value+5,value+6,value+7};
  if (zero_counters) {
    counts[0].instructions=counts[0].cycles=0;
    counts[1].instructions=counts[1].cycles=0;
  }
  if (fail) { errno = ENOTSUP; return -1; }
  return 0;
}
static std::string contents(const std::string& path) {
  std::ifstream file(path); return {std::istreambuf_iterator<char>(file),{}};
}
int main(int argc,char** argv) {
  assert(argc==2);
  R r; int clocks=0;
  auto clock = [&] { return static_cast<std::uint64_t>(++clocks); };
  r.Configure(nullptr,read_counts,2,125,3); r.Record(1,clock);
  assert(!calls && !clocks && r.FlushAfterJoin()==R::Result::Disabled);
  r.ConfigureApple(nullptr); r.Record(1,clock); assert(!calls && !clocks);
  const std::string path = std::string(argv[1])+"/work.csv";
  r.Configure(path.c_str(),read_counts,2,125,3);
  std::thread writer([&] {
    r.Record(10,clock); value=1; r.Record(20,clock); // Preserve resets as raw evidence.
    fail=true; r.Record(30,clock); r.Record(40,clock);
  }); writer.join();
  assert(calls==3 && clocks==6 && r.Size()==3 && r.Dropped()==1);
  assert(r.At(0).levels[0].instructions==100 && r.At(1).levels[0].instructions==1);
  assert(r.At(2).error==ENOTSUP && r.At(2).levels[0].instructions==0);
  assert(contents(path).empty());
  assert(r.FlushAfterJoin()==R::Result::Saved);
  const auto saved=contents(path);
  assert(saved.find("# dropped=1 levels=2 timebase=125/3 config_error=0\n")==0);
  r.Record(50,clock); assert(calls==3 && clocks==6);
  assert(r.FlushAfterJoin()==R::Result::Saved && contents(path)==saved);
  r.Configure(path.c_str(),nullptr,2,125,3); r.Record(60,clock);
  assert(r.At(0).error==ENOSYS && calls==3 && clocks==6);
  assert(r.FlushAfterJoin()==R::Result::OpenFailed && contents(path)==saved);
  r.Configure((path+".invalid").c_str(),read_counts,9,125,0); r.Record(70,clock);
  assert(r.At(0).error==EINVAL && calls==3 && clocks==6);
  assert(r.FlushAfterJoin()==R::Result::Saved);
  fail=false;zero_counters=true;
  r.Configure((path+".unsupported").c_str(),read_counts,2,125,3);r.Record(80,clock);
  assert(r.At(0).error==ENOTSUP && r.At(0).levels[0].instructions==0);
  assert(r.At(0).levels[0].user_mach==value+2); // Keep raw non-PMU evidence.
}
