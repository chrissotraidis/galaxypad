#!/usr/bin/env python3
"""Generate isolated, default-off Simulator gameplay inversion experiment."""
from pathlib import Path
import json
import sys
root=Path(__file__).resolve().parents[2]
variant2='--retain-neutral-base' in sys.argv[1:]
out=root/('generated/experiments/pointer-gameplay-pass2-v2-20260913' if variant2 else
          'generated/experiments/pointer-gameplay-pass2-20260913')
out.mkdir(parents=True,exist_ok=True)
canonical=root/'apple/ios/GalaxyPadCoreHost.mm'
source=canonical.read_text()
source=source.replace('namespace {', '#if TARGET_OS_SIMULATOR\n#include "'+str(root/'experiments/pointer/NeutralGameplayReadiness.h')+'"\n#endif\n\nnamespace {',1)
source=source.replace('  bool pointerMotionInvalidated=false;', '''  galaxypad::experimental::NeutralGameplayReadiness gameplayReadiness;
  bool gameplayMotionLatched=false;
  std::optional<std::pair<float,float>> gameplayCachedInput, gameplayCachedResult;
  bool pointerMotionInvalidated=false;''',1)
source=source.replace('      _session->pointerConfiguration.reset();', '''      _session->pointerConfiguration.reset();
      _session->gameplayReadiness.reset();
      _session->gameplayCachedInput.reset();''',1)
marker='  if (pitch22Profile && pointerProbe &&'
source=source.replace(marker, '''  const bool gameplayPointer=!pitch22Profile &&
    [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevNeutralGameplayTouch"];
  if (gameplayPointer) {
    std::weak_ptr<Session> weakSession=session;
    session->mixer->setTouchPointerMapper([weakSession](const galaxypad::InputState& touch,
        const galaxypad::InputState& merged)->std::optional<std::pair<float,float>> {
      const auto original=std::pair{touch.pointerX,touch.pointerY};
      auto owner=weakSession.lock();
      if(!owner) return original;
      std::lock_guard lock(owner->pointerConfigurationMutex);
      if ((merged.buttons&galaxypad::Spin) || merged.tiltX!=0 || merged.tiltY!=0) {
        owner->gameplayMotionLatched=true;
        owner->gameplayReadiness.reset();
        owner->pointerConfiguration.reset();
        owner->gameplayCachedInput.reset();
      }
      auto age=std::chrono::steady_clock::now()-owner->pointerConfigurationTime;
      if (!touch.pointerVisible || !owner->pointerConfiguration ||
          age<decltype(age)::zero() || age>std::chrono::milliseconds(100)) {
        owner->gameplayCachedInput.reset();
        return original;
      }
      if (owner->gameplayCachedInput!=original) {
        owner->gameplayCachedInput=original;
        auto result=galaxypad::InvertPointer({touch.pointerX,touch.pointerY},
          [&](galaxypad::PointerPoint point) {
            return galaxypad::ProjectMenuPointer(point,*owner->pointerConfiguration,
              [](const Common::Matrix44& transform) {
                return WiimoteEmu::CameraLogic::GetCameraPoints(transform,
                  {WiimoteEmu::CameraLogic::CAMERA_FOV_X,WiimoteEmu::CameraLogic::CAMERA_FOV_Y});
              });
          });
        owner->gameplayCachedResult=result ? std::optional(std::pair{result->x,result->y}) : std::nullopt;
      }
      // Preserve baseline outside supported/reachable neutral coordinates.
      return owner->gameplayCachedResult.value_or(original);
    });
    NSLog(@"[GalaxyPad pointer experiment] neutral gameplay opt-in; mode25 pitch20, cooldown180 fields, cached inverse");
  }
''' + marker,1)
source=source.replace('          if (pointerProbe) {','          if (pointerProbe && !gameplayPointer) {',1)
marker='          // Read presenter geometry on its rendering thread, not from UIKit.'
source=source.replace(marker, '''#if TARGET_OS_SIMULATOR
          Common::EventHook gameplayPointerHook;
          if (gameplayPointer) {
            NSData *dol=[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:@"sys/main.dol"]];
            unsigned char digest[CC_SHA256_DIGEST_LENGTH];
            NSMutableString *hash=[NSMutableString string];
            if(dol.length==6283264) {
              CC_SHA256(dol.bytes,(CC_LONG)dol.length,digest);
              for(unsigned char byte:digest) [hash appendFormat:@"%02x",byte];
            }
            if([hash isEqualToString:@(GalaxyPadDOLSHA256)]) {
              gameplayPointerHook=GetVideoEvents().vi_end_field_event.Register(
                [session,fields=uint64_t(0),previousReady=false,transitionRecords=0u]() mutable {
                  if(!Core::IsCPUThread()) return;
                  ++fields;
                  auto& system=Core::System::GetInstance();
                  auto& memory=system.GetMemory();
                  auto read=[&](uint32_t address)->std::optional<uint32_t> {
                    const bool mem2=address>=0x90000000u;
                    const uint32_t base=mem2?0x90000000u:0x80000000u;
                    const uint32_t size=mem2?memory.GetExRamSizeReal():memory.GetRamSizeReal();
                    const auto* bytes=mem2?memory.GetEXRAM():memory.GetRAM();
                    if(!bytes || address<base || uint64_t(address-base)+4>size) return std::nullopt;
                    bytes+=address-base;
                    return (uint32_t(bytes[0])<<24)|(uint32_t(bytes[1])<<16)|
                      (uint32_t(bytes[2])<<8)|uint32_t(bytes[3]);
                  };
                  galaxypad::experimental::NeutralGameplaySnapshot snapshot;
                  snapshot.exactDolVerified=snapshot.pitch20ProfileVerified=true;
                  snapshot.currentField=snapshot.observationField=fields;
                  snapshot.context=galaxypad::ReadPointerContext(system.GetPowerPC().GetPPCState().gpr[13],read);
                  snapshot.calibration=galaxypad::ReadPointerCalibration(read);
                  snapshot.conversion=galaxypad::ReadPointerConversionInputs(read);
                  // Lock order: never acquire mixer while holding configuration.
                  const auto [touch,controller]=session->mixer->diagnosticSnapshot();
                  snapshot.controllerAim=controller.pointerVisible;
                  snapshot.motionActiveOrLatched=((touch.buttons|controller.buttons)&galaxypad::Spin) ||
                    touch.tiltX!=0 || touch.tiltY!=0 || controller.tiltX!=0 || controller.tiltY!=0;
                  std::lock_guard lock(session->pointerConfigurationMutex);
                  snapshot.motionActiveOrLatched|=session->gameplayMotionLatched;
                  session->gameplayMotionLatched=false;
                  auto configuration=session->gameplayReadiness.observe(snapshot);
                  if(configuration.has_value()!=previousReady && transitionRecords<32) {
                    ++transitionRecords;
                    GalaxyPadLogPerformanceWindow(@[[NSString stringWithFormat:
                      @"pointer_gameplay_experiment field=%llu ready=%d mode=%u",
                      (unsigned long long)fields,configuration.has_value(),
                      snapshot.context?snapshot.context->mode:0]]);
                  }
                  previousReady=configuration.has_value();
                  if(!configuration) session->gameplayCachedInput.reset();
                  session->pointerConfiguration=configuration;
                  session->pointerConfigurationTime=std::chrono::steady_clock::now();
                });
            }
          }
#endif
''' + marker,1)
target=out/'GalaxyPadCoreHost.mm'
if variant2:
    source=source.replace('gameplayReadiness;', 'gameplayReadiness{true};',1)
    source=source.replace('if ((merged.buttons&galaxypad::Spin) || merged.tiltX!=0 || merged.tiltY!=0) {',
                          'if (merged.tiltX!=0 || merged.tiltY!=0) {',1)
    source=source.replace('snapshot.motionActiveOrLatched=((touch.buttons|controller.buttons)&galaxypad::Spin) ||',
                          'snapshot.motionActiveOrLatched=',1)
    source=source.replace('neutral gameplay opt-in; mode25 pitch20, cooldown180 fields, cached inverse',
                          'neutral gameplay candidate2; mode25 pitch20, retained neutral Point base through Spin, cached inverse',1)
target.write_text(source)
(out/'overlay.json').write_text(json.dumps({'version':0,'use-external-names':False,'roots':[{'type':'file','name':str(canonical),'external-contents':str(target)}]},indent=2)+'\n')
print(target)
