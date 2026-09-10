// Exercise the actual mod logger with deterministic clocks and stubbed decoding.
#include <time.h>
#include <assert.h>
#include <math.h>
static double wall_time=100,cpu_time=1,wall_step,cpu_step;
static int cpu_unavailable,fallback_mode,clock_calls;
static int test_clock(clockid_t clock,struct timespec *t) {
    clock_calls++;
    if(clock==CLOCK_THREAD_CPUTIME_ID && cpu_unavailable)return -1;
    double v=clock==CLOCK_THREAD_CPUTIME_ID?cpu_time:wall_time;
    t->tv_sec=(time_t)v;t->tv_nsec=(long)((v-t->tv_sec)*1e9);return 0;
}
#define clock_gettime test_clock
#include "../apple/shared/GalaxyPadTHPMod.c"
#undef clock_gettime
struct GalaxyPadTHPDecoder { int unused; };
static struct GalaxyPadTHPDecoder stub;
GalaxyPadTHPDecoder *GalaxyPadTHPDecoderCreate(void){return &stub;}
void GalaxyPadTHPDecoderDestroy(GalaxyPadTHPDecoder *d){(void)d;}
int GalaxyPadTHPDispatchInner(CPUState *s,GalaxyPadTHPDecoder *d) {
    (void)d;wall_time+=wall_step;cpu_time+=cpu_step;
    s->pc=fallback_mode?0x8045239c:s->lr;return 1;
}
static void near(double a,double b){assert(fabs(a-b)<0.00001);}
int main(void) {
    setenv("GALAXYPAD_THP_TIMING","1",1);unsetenv("STATICRECOMP_LOCKSTEP");
    load(NULL);CPUState s={0};s.lr=0x80451750;
    wall_step=.063;cpu_step=.003;decode(&s);
    assert(accepted==1 && rejected==0 && window_calls==1 && cpu_calls==1);
    near(max_ms,63);near(cpu_at_max_wall_ms,3);
    wall_step=.010;cpu_step=.009;decode(&s);
    near(max_ms,63);near(cpu_at_max_wall_ms,3);near(total_cpu_ms,12);
    cpu_unavailable=1;fallback_mode=1;wall_step=.001;decode(&s);
    assert(window_rejected==1 && cpu_calls==2 && rejected==1);
    near(window_end-window_start,.074);
    wall_time+=60; // Unload must report this separately, not as decode span.
    unload();assert(window_calls==0 && cpu_calls==0 && decoder==NULL);
    cpu_unavailable=0;fallback_mode=0;wall_step=.003;cpu_step=.002;
    setenv("GALAXYPAD_THP_TIMING","0",1);load(NULL);
    int before=clock_calls;decode(&s);assert(clock_calls==before);
    assert(accepted==1 && window_calls==0);unload();
    setenv("GALAXYPAD_THP_TIMING","1",1);load(NULL);
    wall_step=5.1;decode(&s);assert(window_calls==0);unload();
    puts("THP timing tests passed");
}
