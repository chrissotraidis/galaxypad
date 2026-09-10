// Ordinary Mach task-access preflight on an owned, self-terminating child.
// No thread/task suspension, target writes, injection, or privilege changes.
#include <mach/mach.h>
#include <mach/arm/thread_status.h>
#include <pthread.h>
#include <sys/wait.h>
#include <unistd.h>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <map>

using Clock = std::chrono::steady_clock;
__attribute__((noinline)) static unsigned work(unsigned value) {
  for (unsigned i=0;i<10000;++i) {
    value=value*1664525u+1013904223u;
    asm volatile("" : "+r"(value));
  }
  return value;
}

int main(int argc,char** argv) {
  if(argc==2 && std::strcmp(argv[1],"--workload")==0){
    pthread_setname_np("GalaxyPad PC preflight");
    unsigned value=1;
    const auto end=Clock::now()+std::chrono::seconds(8);
    while(Clock::now()<end)value=work(value);
    std::printf("workload_result=%u\n",value);
    return 0;
  }
  if(argc!=1){std::fprintf(stderr,"usage: %s [--workload]\n",argv[0]);return 1;}
  const pid_t child=fork();
  if(child<0){perror("fork");return 1;}
  if(child==0){
    pthread_setname_np("GalaxyPad PC preflight");
    unsigned value=1;
    const auto end=Clock::now()+std::chrono::seconds(2);
    while(Clock::now()<end)value=work(value);
    _exit(value==0?1:0);
  }
  task_t task=MACH_PORT_NULL;
  const kern_return_t access=task_for_pid(mach_task_self(),child,&task);
  std::printf("owned_child=%d task_for_pid=%d (%s)\n",child,access,mach_error_string(access));
  std::map<uint64_t,unsigned> pcs;
  unsigned reads=0,failures=0;
  if(access==KERN_SUCCESS){
    thread_act_array_t threads=nullptr;
    mach_msg_type_number_t count=0;
    const auto result=task_threads(task,&threads,&count);
    std::printf("task_threads=%d count=%u\n",result,count);
    if(result==KERN_SUCCESS){
      const auto end=Clock::now()+std::chrono::milliseconds(500);
      while(Clock::now()<end){
        for(unsigned i=0;i<count;++i){
          arm_thread_state64_t state{};
          mach_msg_type_number_t words=ARM_THREAD_STATE64_COUNT;
          // Kernel provides the register snapshot; no externally held suspend.
          const auto status=thread_get_state(threads[i],ARM_THREAD_STATE64,
                            reinterpret_cast<thread_state_t>(&state),&words);
          if(status==KERN_SUCCESS){++pcs[arm_thread_state64_get_pc(state)];++reads;}
          else ++failures;
        }
        usleep(2000);
      }
      for(unsigned i=0;i<count;++i)mach_port_deallocate(mach_task_self(),threads[i]);
      vm_deallocate(mach_task_self(),reinterpret_cast<vm_address_t>(threads),
                    count*sizeof(thread_t));
    }
    mach_port_deallocate(mach_task_self(),task);
  }
  int status=0;
  if(waitpid(child,&status,0)!=child){perror("waitpid");return 1;}
  std::printf("reads=%u failures=%u unique_pcs=%zu child_exit=%d\n",reads,failures,
              pcs.size(),WIFEXITED(status)?WEXITSTATUS(status):-1);
  for(const auto& [pc,count]:pcs)std::printf("pc=0x%llx observations=%u\n",
      static_cast<unsigned long long>(pc),count);
  return access==KERN_SUCCESS && reads>0 && failures==0 ? 0 : 2;
}
