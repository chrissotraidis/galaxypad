#include "GalaxyPadTHPMod.h"
#include "GalaxyPadTHPGuest.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static GalaxyPadTHPDecoder *decoder;
static unsigned accepted,rejected;
static int timing;
static double window_start,window_end,total_ms,max_ms;
static unsigned window_calls,window_rejected;
static double total_cpu_ms,cpu_at_max_wall_ms;
static unsigned cpu_calls;
static double thread_cpu_seconds(void) {
    struct timespec t;
    if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)!=0)return -1;
    return t.tv_sec+t.tv_nsec*1e-9;
}
static double monotonic_seconds(void) {
    struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
    return t.tv_sec+t.tv_nsec*1e-9;
}
static void flush_timing(double now) {
    if(!window_calls)return;
    struct timespec wall;clock_gettime(CLOCK_REALTIME,&wall);
    fprintf(stderr,"[galaxypad-native-thp timing] epoch=%.6f mono=%.6f seconds=%.3f idle_since_last_call=%.3f calls=%u fallback=%u dispatch_mean_ms=%.3f dispatch_max_ms=%.3f cpu_calls=%u cpu_mean_ms=%.3f cpu_at_max_wall_ms=%.3f\n",
            wall.tv_sec+wall.tv_nsec*1e-9,now,window_end-window_start,now-window_end,window_calls,window_rejected,total_ms/window_calls,max_ms,
            cpu_calls,cpu_calls?total_cpu_ms/cpu_calls:-1,cpu_at_max_wall_ms);
    window_start=now;window_calls=window_rejected=0;total_ms=max_ms=0;
    cpu_calls=0;total_cpu_ms=0;cpu_at_max_wall_ms=-1;
}
static void load(const ModernGekkoModHostApi *api) {
    (void)api;accepted=rejected=0;
    const char *diagnostic=getenv("GALAXYPAD_THP_TIMING");
    timing=diagnostic && diagnostic[0]=='1' && diagnostic[1]=='\0';
    window_start=monotonic_seconds();window_calls=window_rejected=0;total_ms=max_ms=0;
    cpu_calls=0;total_cpu_ms=0;cpu_at_max_wall_ms=-1;
    // Native writes are not a lockstep shadow implementation. Fail to the
    // original decoder whenever the diagnostic lockstep mode is configured.
    const char *lockstep=getenv("STATICRECOMP_LOCKSTEP");
    decoder=(lockstep && *lockstep)?NULL:GalaxyPadTHPDecoderCreate();
    fprintf(stderr,"[galaxypad-native-thp] candidate initialized=%d\n",decoder!=NULL);
}
static void unload(void) {
    if(timing)flush_timing(monotonic_seconds());
    fprintf(stderr,"[galaxypad-native-thp] accepted=%u fallback=%u\n",accepted,rejected);
    GalaxyPadTHPDecoderDestroy(decoder);decoder=NULL;
}
static void decode(CPUState *s) {
    uint32_t lr=s->lr;
    const double start=timing?monotonic_seconds():0;
    const double cpu_start=timing?thread_cpu_seconds():-1;
    if(!GalaxyPadTHPDispatchInner(s,decoder))return;
    if(timing) {
        const double now=monotonic_seconds(),ms=(now-start)*1000;
        const double cpu_end=thread_cpu_seconds();
        const double cpu_ms=cpu_start>=0 && cpu_end>=cpu_start?(cpu_end-cpu_start)*1000:-1;
        if(cpu_ms>=0){total_cpu_ms+=cpu_ms;cpu_calls++;}
        if(!window_calls)window_start=start;
        window_end=now;
        window_calls++;window_rejected+=(s->pc!=lr);total_ms+=ms;
        if(ms>max_ms){max_ms=ms;cpu_at_max_wall_ms=cpu_ms;}
        if(now-window_start>=5)flush_timing(now);
    }
    if(s->pc==lr) {
        if(!accepted)fprintf(stderr,"[galaxypad-native-thp] first native frame accepted\n");
        accepted++;
    } else rejected++;
}
static const ModernGekkoModPatch patch[]={RECOMP_PATCH(0x80452398,decode)};
static const ModernGekkoModDesc desc={
    .abi_version=MODERNGEKKO_MOD_ABI_VERSION,.cpu_abi_version=MODERNGEKKO_CPU_ABI_VERSION,
    .cpu_state_size=sizeof(CPUState),.game_id="RMGE01",.id="galaxypad.native-thp",
    .version="0.1.0",.display_name="Private native THP candidate",
    .patches=patch,.num_patches=1,.on_load=load,.on_unload=unload
};
const ModernGekkoModDesc *GalaxyPadTHPModDescriptor(void){return &desc;}
