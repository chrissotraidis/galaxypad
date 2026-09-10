// Bounded read-only host counters. Aggregate CPU ticks cannot prove per-core scheduling.
// host_statistics may return cached counters; query timestamps do not establish freshness.
#include <mach/mach.h>
#include <mach/host_info.h>
#include <mach/vm_statistics.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>

using Clock=std::chrono::steady_clock;
static unsigned long long Now() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count();
}
struct Row {
  unsigned long long start,end;
  vm_statistics64_data_t vm{};
  host_cpu_load_info_data_t cpu{};
  bool valid=false;
};
int main(int argc,char** argv) {
  if(argc!=2) {std::fprintf(stderr,"Usage: host-pressure-probe SECONDS(1..120)\n");return 2;}
  char* end=nullptr;const long seconds=std::strtol(argv[1],&end,10);
  if(!*argv[1]||*end||seconds<1||seconds>120) return 2;
  std::vector<Row> rows;rows.reserve(seconds*10+2);
  const mach_port_t host=mach_host_self();
  const auto deadline=Clock::now()+std::chrono::seconds(seconds);
  while(Clock::now()<deadline&&rows.size()<size_t(seconds*10+2)) {
    Row row{};row.start=Now();
    mach_msg_type_number_t vm_count=HOST_VM_INFO64_COUNT,cpu_count=HOST_CPU_LOAD_INFO_COUNT;
    const auto vm_result=host_statistics64(host,HOST_VM_INFO64,
      reinterpret_cast<host_info64_t>(&row.vm),&vm_count);
    const auto cpu_result=host_statistics(host,HOST_CPU_LOAD_INFO,
      reinterpret_cast<host_info_t>(&row.cpu),&cpu_count);
    row.end=Now();
    row.valid=vm_result==KERN_SUCCESS&&cpu_result==KERN_SUCCESS&&
      vm_count==HOST_VM_INFO64_COUNT&&cpu_count==HOST_CPU_LOAD_INFO_COUNT;
    rows.push_back(row);
    if(!row.valid) break;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  }
  mach_port_deallocate(mach_task_self(),host);
  std::puts("start_ns,end_ns,valid,cpu_user_ticks,cpu_system_ticks,cpu_idle_ticks,cpu_nice_ticks,pageins,pageouts,swapins,swapouts,compressions,decompressions");
  bool valid=!rows.empty();
  for(const auto& r:rows) {
    if(!r.valid) {std::printf("%llu,%llu,0,,,,,,,,,,\n",r.start,r.end);valid=false;continue;}
    std::printf("%llu,%llu,1,%u,%u,%u,%u,%llu,%llu,%llu,%llu,%llu,%llu\n",r.start,r.end,
      r.cpu.cpu_ticks[CPU_STATE_USER],r.cpu.cpu_ticks[CPU_STATE_SYSTEM],
      r.cpu.cpu_ticks[CPU_STATE_IDLE],r.cpu.cpu_ticks[CPU_STATE_NICE],
      (unsigned long long)r.vm.pageins,(unsigned long long)r.vm.pageouts,
      (unsigned long long)r.vm.swapins,(unsigned long long)r.vm.swapouts,
      (unsigned long long)r.vm.compressions,(unsigned long long)r.vm.decompressions);
  }
  return valid?0:1;
}
