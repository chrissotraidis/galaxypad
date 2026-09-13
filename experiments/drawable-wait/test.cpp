#include "DrawableWaitProbe.h"
#include <cassert>
using namespace galaxypad::drawable_wait;
int main(){
 int clocks=0,states=0,acquires=0;
 auto clock=[&](){return std::uint64_t(++clocks)*500;};
 auto state=[&](){++states;return State{true,states==1};};
 auto acquire=[&](){++acquires;return 1;};
 assert(Measure(clock,state,acquire)==1);assert(clocks==0&&states==0&&acquires==1);
 assert(!Read());enabled=true;
 assert(Measure(clock,state,acquire)==1);assert(clocks==2&&states==2&&acquires==2);
 assert(totals[Calls]==1&&totals[TotalNs]==500&&totals[BusyToIdle]==1);
 assert(totals[StateCount+3]==1&&totals[BusyToIdleNs]==500);
 for(unsigned i=1;i<120;++i)Record(10000,true,{false,false},{false,false});
 auto snapshot=Read();assert(snapshot&&(*snapshot)[Calls]==120&&(*snapshot)[Nil]==119);
 assert((*snapshot)[HistBegin]==1&&(*snapshot)[HistBegin+1]==119);
 assert((*snapshot)[TotalNs]==1190500&&(*snapshot)[MaxNs]==10000);
 std::uint64_t bins=0,groups=0,ns=0;
 for(unsigned i=0;i<8;++i)bins+=(*snapshot)[HistBegin+i];
 for(unsigned i=0;i<4;++i){groups+=(*snapshot)[StateCount+i];ns+=(*snapshot)[StateNs+i];}
 assert(bins==120&&groups==120&&ns==(*snapshot)[TotalNs]);
 Record(16000000,false,{true,false},{false,true});
 assert(totals[HistBegin+7]==1&&totals[PendingChanged]==1&&totals[BusyAfter]==1);
 assert(Read()->at(Calls)==120);
 for(unsigned i=121;i<20000;++i)Record(1,false,{false,false},{false,false});
 assert(publications==128&&Read()->at(Calls)==15360);
 enabled=false;Measure(clock,state,acquire);assert(clocks==2&&states==2&&acquires==3);
}
