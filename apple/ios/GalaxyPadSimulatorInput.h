// SPDX-License-Identifier: GPL-3.0-or-later
// Simulator diagnostic input, never included by the physical-device host.
#pragma once
#import <Foundation/Foundation.h>
#include "../shared/GalaxyPadInput.h"

// Full snapshots with short leases: stale/malformed input always becomes neutral.
// A lifecycle reset advances notBefore so an old command cannot revive a hold.
static inline galaxypad::InputState GalaxyPadReadSimulatorInput(
    NSString *path, double now, double notBefore) {
  galaxypad::InputState neutral;
  NSDictionary *attributes=[NSFileManager.defaultManager attributesOfItemAtPath:path error:nil];
  if (![attributes[NSFileType] isEqual:NSFileTypeRegular] ||
      [attributes[NSFileSize] unsignedLongLongValue]>4096) return neutral;
  NSData *data=[NSData dataWithContentsOfFile:path];
  if (!data || data.length>4096) return neutral;
  id json=[NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
  if (![json isKindOfClass:NSDictionary.class]) return neutral;
  NSDictionary *values=json;
  auto number=[&](NSString *key, double fallback) -> double {
    id value=values[key];
    return value==nil ? fallback : [value isKindOfClass:NSNumber.class] ?
      [value doubleValue] : NAN;
  };
  double issued=number(@"issued",NAN), expires=number(@"expires",NAN);
  double buttons=number(@"buttons",0);
  if (!std::isfinite(issued) || !std::isfinite(expires) ||
      issued<=notBefore || issued>now || expires<=now || expires-issued>2 ||
      !std::isfinite(buttons) || buttons<0 || buttons>8191 || std::floor(buttons)!=buttons)
    return neutral;
  galaxypad::InputState result;
  result.buttons=(uint32_t)buttons;
  struct Field { NSString *key; float *target; double minimum, maximum, fallback; };
  Field fields[]={
    {@"moveX",&result.moveX,-1,1,0}, {@"moveY",&result.moveY,-1,1,0},
    {@"tiltX",&result.tiltX,-1,1,0}, {@"tiltY",&result.tiltY,-1,1,0},
    {@"pointerX",&result.pointerX,0,1,0.5}, {@"pointerY",&result.pointerY,0,1,0.5}};
  for (auto field:fields) {
    double value=number(field.key,field.fallback);
    if (!std::isfinite(value) || value<field.minimum || value>field.maximum) return neutral;
    *field.target=(float)value;
  }
  double visible=number(@"pointerVisible",0);
  if (visible!=0 && visible!=1) return neutral;
  result.pointerVisible=visible==1;
  result.connected=true;
  return result;
}
