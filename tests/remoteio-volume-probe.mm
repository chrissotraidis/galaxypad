// SPDX-License-Identifier: GPL-3.0-or-later
// Standalone capability probe. Does not start audio or modify app preferences.
#import <Foundation/Foundation.h>
#import <AudioToolbox/AudioToolbox.h>
#include <cstdio>
int main() {
  @autoreleasepool {
    AudioComponentDescription description{};
    description.componentType=kAudioUnitType_Output;
    description.componentSubType=kAudioUnitSubType_RemoteIO;
    description.componentManufacturer=kAudioUnitManufacturer_Apple;
    auto component=AudioComponentFindNext(nullptr,&description);
    if (!component) return 1;
    AudioUnit unit=nullptr;
    OSStatus created=AudioComponentInstanceNew(component,&unit);
    if (created || !unit) return 2;
    // Match the existing backend's parameter/scope/element, before Initialize.
    OSStatus set=AudioUnitSetParameter(unit,kHALOutputParam_Volume,kAudioUnitScope_Output,0,0,0);
    AudioUnitParameterValue value=-1;
    OSStatus get=AudioUnitGetParameter(unit,kHALOutputParam_Volume,kAudioUnitScope_Output,0,&value);
    std::printf("RemoteIO HAL volume: set=%d get=%d value=%g\n",int(set),int(get),double(value));
    AudioComponentInstanceDispose(unit);
    return 0; // A rejected parameter is an observation, not a probe failure.
  }
}
