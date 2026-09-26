#include "PrecisionTimingProbe.h"
#include <cassert>
#include <numeric>
using namespace galaxypad::precision_timing;
int main(){
 Counters c{};Record(c,100,200,230,180,40,true);
 assert(c[Calls]==1&&c[Positive]==1&&c[RequestedNs]==100&&c[WallNs]==130&&c[SpinNs]==50&&c[CpuNs]==40&&c[OvershootNs]==30);
 Record(c,300,200,310,305,90,false);
 assert(c[Late]==1&&c[CpuValid]==1&&c[CpuNs]==40&&c[RequestedNs]==100);
 assert(std::accumulate(c.begin()+HistBegin,c.end(),0ULL)==1&&c[OvershootNs]==30);
 {Scope s(0);{Scope t(1);assert(lane==1);}assert(lane==0);}assert(lane==-1);
 enabled=false;{Scope s(0);Measurement m(std::chrono::steady_clock::now());assert(!m.active);m.Spin();}
 assert(!Read(0));assert(totals[Calls]==0);
 enabled=true;{Scope s(0);for(unsigned i=0;i<120;++i){if(i==119)lastPublication=0;Measurement m(std::chrono::steady_clock::now());m.Spin();}}
 assert(Read(0)&&(*Read(0))[Calls]==120);assert(!Read(1));
 auto snapshot=Read(0);lanes[0].sequence.fetch_add(1);assert(!Read(0));lanes[0].sequence.fetch_add(1);assert(Read(0)==snapshot);
 publications=512;lastPublication=0;{Scope s(0);for(unsigned i=0;i<120;++i){Measurement m(std::chrono::steady_clock::now());m.Spin();}}assert(Read(0)==snapshot);
}
