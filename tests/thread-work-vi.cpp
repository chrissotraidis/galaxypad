#include "vi-timing-recorder.h"
#include <cassert>
#include <cstdlib>
#include <string>
#include <thread>
int main(int argc,char** argv) {
  assert(argc==2);
  const std::string path=std::string(argv[1])+"/vi.csv", work=path+".work";
  assert(setenv("GALAXYPAD_THREAD_WORK_TIMING",work.c_str(),1)==0);
  galaxypad::ViTimingRecorder recorder;
  recorder.Configure(path.c_str());
  std::thread writer([&] {
    recorder.Record();
    volatile unsigned value=1;
    for(unsigned i=0;i<100000;++i) value=value*1664525+1013904223;
    recorder.Record();
  }); writer.join();
  assert(recorder.FlushAfterJoin()==galaxypad::ViTimingRecorder::Result::Saved);
}
