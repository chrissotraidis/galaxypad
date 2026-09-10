#include "../apple/shared/GalaxyPadMovementTrace.h"
int main() {
  galaxypad::MovementTrace trace("test");
  trace.record(0,0);
  trace.record(1,-.5f);
  trace.record(1,-.5f);
  trace.record(0,0);
  for (unsigned i=0;i<300;++i) trace.record(i%2,0);
}
