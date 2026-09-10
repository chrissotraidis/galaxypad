// Read-only, bounded macOS thread-state sampling. No suspension or priority changes.
// TH_STATE_RUNNING does not distinguish on-core execution from runnable scheduling.
// pth_{user,system}_time are nanoseconds, populated from THREAD_BASIC_INFO:
// https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/bsd_kern.c
// fill_taskthreadinfo converts seconds/microseconds to NSEC units.
#include <libproc.h>
#include <sys/proc_info.h>
#include <mach/thread_info.h>
#include <pthread.h>
#include <unistd.h>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <thread>
#include <vector>

using Clock = std::chrono::steady_clock;
using namespace std::chrono_literals;
static unsigned long long Now() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count();
}
struct Row {
  unsigned long long start, end;
  proc_threadinfo info{};
  bool valid;
};
static uint64_t FindThread(int pid, const char* name) {
  // Refuse truncation rather than silently selecting from an incomplete list.
  std::vector<uint64_t> ids(4096);
  const int bytes = proc_pidinfo(pid, PROC_PIDLISTTHREADS, 0, ids.data(), int(ids.size()*sizeof(uint64_t)));
  if (bytes <= 0 || bytes % sizeof(uint64_t) || size_t(bytes) >= ids.size()*sizeof(uint64_t))
    throw std::runtime_error("Cannot obtain a complete thread list");
  uint64_t found=0;unsigned matches=0;
  for (size_t i=0;i<size_t(bytes)/sizeof(uint64_t);++i) {
    proc_threadinfo info{};
    if (proc_pidinfo(pid, PROC_PIDTHREADINFO, ids[i], &info, sizeof(info)) == sizeof(info) &&
        strnlen(info.pth_name,sizeof(info.pth_name)) < sizeof(info.pth_name) &&
        !std::strcmp(info.pth_name,name)) {found=ids[i];++matches;}
  }
  if(matches!=1) throw std::runtime_error("Expected exactly one matching thread name");
  return found;
}
static std::vector<Row> Capture(int pid,uint64_t id,const char* name,int milliseconds,int period_ms) {
  std::vector<Row> rows;
  const size_t cap=size_t(milliseconds/period_ms)+2;
  rows.reserve(cap);
  const auto end=Clock::now()+std::chrono::milliseconds(milliseconds);
  while(Clock::now()<end && rows.size()<cap) {
    Row row{};row.start=Now();
    const int bytes=proc_pidinfo(pid,PROC_PIDTHREADINFO,id,&row.info,sizeof(row.info));
    row.end=Now();
    row.valid=bytes==sizeof(row.info) &&
      strnlen(row.info.pth_name,sizeof(row.info.pth_name))<sizeof(row.info.pth_name) &&
      !std::strcmp(row.info.pth_name,name);
    rows.push_back(row);
    if(!row.valid) break; // No fabricated zero states and no thread reacquisition.
    std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
  }
  return rows;
}
static int SelfTest() {
  std::atomic<bool> ready{false},stop{false},busy{false};
  std::thread worker([&] {
    pthread_setname_np("gpad-state-probe");ready=true;
    while(!stop.load()) {
      if(!busy.load()) std::this_thread::sleep_for(1ms);
      else std::atomic_signal_fence(std::memory_order_seq_cst);
    }
  });
  int result=1;
  try {
    while(!ready.load()) std::this_thread::yield();
    const auto id=FindThread(getpid(),"gpad-state-probe");
    const auto waiting=Capture(getpid(),id,"gpad-state-probe",200,2);
    busy=true;
    const auto running=Capture(getpid(),id,"gpad-state-probe",200,2);
    unsigned waits=0,runs=0;
    for(const auto& r:waiting) if(r.valid&&r.info.pth_run_state==TH_STATE_WAITING) ++waits;
    for(const auto& r:running) if(r.valid&&r.info.pth_run_state==TH_STATE_RUNNING) ++runs;
    if(!waits||!runs) throw std::runtime_error("Did not observe both known test states");
    const auto cpu_delta=[](const std::vector<Row>& rows) {
      const auto& a=rows.front().info;const auto& b=rows.back().info;
      if(b.pth_user_time<a.pth_user_time||b.pth_system_time<a.pth_system_time)
        throw std::runtime_error("CPU counters decreased");
      return b.pth_user_time-a.pth_user_time+b.pth_system_time-a.pth_system_time;
    };
    const auto wait_cpu=cpu_delta(waiting),run_cpu=cpu_delta(running);
    if(run_cpu<=wait_cpu || run_cpu>running.back().end-running.front().start+10000000ULL)
      throw std::runtime_error("CPU nanosecond counter self-test failed");
    std::printf("CPU-time self-test: waiting_ns=%llu busy_ns=%llu\n",
                (unsigned long long)wait_cpu,(unsigned long long)run_cpu);
    bool rejected=false;
    try {FindThread(getpid(),"nonexistent-gpad-thread");} catch(...) {rejected=true;}
    if(!rejected) throw std::runtime_error("Missing thread accepted");
    std::printf("Thread-state API self-test: waiting=%u running=%u; missing name rejected\n",waits,runs);
    result=0;
  } catch(const std::exception& e) {std::fprintf(stderr,"%s\n",e.what());}
  stop=true;worker.join();return result;
}
int main(int argc,char** argv) {
  if(argc==2&&!std::strcmp(argv[1],"--self-test")) return SelfTest();
  if(argc!=4&&argc!=5) {std::fprintf(stderr,"Usage: thread-state-probe PID SECONDS PERIOD_MS [THREAD_NAME] | --self-test\n");return 2;}
  try {
    auto number=[](const char* s) {char* end=nullptr;long v=std::strtol(s,&end,10);
      if(!*s||*end||v<=0||v>2147483647L) throw std::runtime_error("Invalid positive integer");return int(v);};
    const int pid=number(argv[1]),seconds=number(argv[2]),period=number(argv[3]);
    if(seconds>120||period<2||period>100) throw std::runtime_error("Bounds: <=120s, period2..100ms");
    char path[PROC_PIDPATHINFO_MAXSIZE]{};
    if(proc_pidpath(pid,path,sizeof(path))<=0) throw std::runtime_error("Cannot resolve process path");
    const char* leaf=std::strrchr(path,'/');
    if(!leaf||(std::strcmp(leaf+1,"GalaxyPadRunner")&&std::strcmp(leaf+1,"GalaxyPad")))
      throw std::runtime_error("Target is not GalaxyPadRunner or GalaxyPad");
    proc_bsdinfo before{},after{};
    if(proc_pidinfo(pid,PROC_PIDTBSDINFO,0,&before,sizeof(before))!=sizeof(before))
      throw std::runtime_error("Cannot read process birth identity");
    const char* name=argc==5?argv[4]:"CPU thread";
    if(std::strcmp(name,"CPU thread")&&std::strcmp(name,"Video thread"))
      throw std::runtime_error("Only CPU thread or Video thread may be captured");
    const auto id=FindThread(pid,name);
    const auto rows=Capture(pid,id,name,seconds*1000,period);
    if(proc_pidinfo(pid,PROC_PIDTBSDINFO,0,&after,sizeof(after))!=sizeof(after)||
       before.pbi_start_tvsec!=after.pbi_start_tvsec||before.pbi_start_tvusec!=after.pbi_start_tvusec)
      throw std::runtime_error("Target process identity changed during capture");
    std::printf("# pid=%d thread_handle=%llu period_ms=%d\n",pid,(unsigned long long)id,period);
    std::printf("# thread_name=%s cpu_time_unit=nanoseconds\n",name);
    std::puts("start_ns,end_ns,valid,run_state,user_time_raw,system_time_raw,cpu_usage,flags,priority,policy,base_priority,max_priority");
    bool valid=!rows.empty();
    for(const auto& r:rows) {
      if(!r.valid) {std::printf("%llu,%llu,0,,,,,,,,,\n",r.start,r.end);valid=false;continue;}
      std::printf("%llu,%llu,1,%d,%llu,%llu,%d,%d,%d,%d,%d,%d\n",r.start,r.end,r.info.pth_run_state,
        (unsigned long long)r.info.pth_user_time,(unsigned long long)r.info.pth_system_time,
        r.info.pth_cpu_usage,r.info.pth_flags,r.info.pth_curpri,
        r.info.pth_policy,r.info.pth_priority,r.info.pth_maxpriority);
    }
    return valid?0:1;
  } catch(const std::exception& e) {std::fprintf(stderr,"%s\n",e.what());return 1;}
}
