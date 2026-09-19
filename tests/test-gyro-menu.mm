// SPDX-License-Identifier: GPL-3.0-or-later
#import "../apple/ios/GalaxyPadGameOverlay.h"
#import "../apple/shared/GalaxyPadSettings.h"
#include <cassert>
#include <cstdio>
@interface GalaxyPadGameOverlay (GyroMenuTest)
- (UIMenu *)gyroMenu;
- (UIMenu *)buildMenu;
- (void)selectRideTiltMode:(galaxypad::TiltMode)mode;
@end
static void press(UIAction *action) {
  UIButton *button=[UIButton buttonWithType:UIButtonTypeSystem primaryAction:action];
  [button sendActionsForControlEvents:UIControlEventTouchUpInside];
}
int main() { @autoreleasepool {
  GalaxyPadSettings *settings=GalaxyPadSettings.sharedSettings;
  settings.gyroPointerSource=GalaxyPadGyroPointerOff;
  GalaxyPadGameOverlay *overlay=[[GalaxyPadGameOverlay alloc] initWithFrame:CGRectMake(0,0,1024,768)];
  __block unsigned changed=0,recenter=0;
  overlay.gyroSettingsChanged=^{++changed;};
  overlay.gyroRecenterRequested=^{++recenter;};
  UIMenu *menu=[overlay gyroMenu];
  assert(menu.children.count==5);
  UIAction *off=(UIAction *)menu.children[0];
  assert(off.state==UIMenuElementStateOn);
  assert(((UIAction *)menu.children[4]).attributes & UIMenuElementAttributesDisabled);
  press((UIAction *)menu.children[1]);
  assert(settings.gyroPointerSource==GalaxyPadGyroPointerDevice && changed==1);
  menu=[overlay gyroMenu];
  assert(((UIAction *)menu.children[1]).state==UIMenuElementStateOn);
  press((UIAction *)menu.children[4]);assert(recenter==1);
  press((UIAction *)menu.children[2]);assert(settings.gyroPointerSource==GalaxyPadGyroPointerController && changed==2);
  UIMenu *response=(UIMenu *)menu.children[3];
  press((UIAction *)response.children[0]);assert(settings.gyroPointerSensitivity==.5);
  BOOL invert=settings.gyroPointerInvertY;
  press((UIAction *)response.children.lastObject);assert(settings.gyroPointerInvertY!=invert);
  overlay.gyroStatus=@"Waiting for motion";
  assert([[[overlay gyroMenu] subtitle] isEqualToString:@"Waiting for motion"]);
  __block galaxypad::TiltMode mode=galaxypad::TiltMode::Normal;
  overlay.tiltModeChanged=^(galaxypad::TiltMode selected) { mode=selected; };
  [overlay selectRideTiltMode:galaxypad::TiltMode::StarBall];
  assert(overlay.rideTiltMode==mode && mode==galaxypad::TiltMode::StarBall);
  // Build the real Controls menu and select Normal through its actual action.
  BOOL gyroFound=NO,rideFound=NO;
  for(UIMenuElement *element in [overlay buildMenu].children) {
    if(![element.title isEqualToString:@"Controls"]) continue;
    for(UIMenuElement *child in ((UIMenu *)element).children) {
      if([child.title isEqualToString:@"Gyro Cursor"]) gyroFound=YES;
      if([child.title isEqualToString:@"Stick Mode (Touch / Controller)"]) {
        rideFound=YES;press((UIAction *)((UIMenu *)child).children[0]);
      }
    }
  }
  assert(gyroFound && rideFound && mode==galaxypad::TiltMode::Normal);
  press((UIAction *)menu.children[0]);assert(settings.gyroPointerSource==GalaxyPadGyroPointerOff);
  puts("Gyro/ride UIKit menu: real action dispatch, toggle state, settings, recenter, status and mode callbacks pass");
  return 0;
} }
