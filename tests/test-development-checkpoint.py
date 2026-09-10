"""Source-contract checks only; actual state write/load needs a live Simulator."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
host = (root / 'apple/ios/GalaxyPadCoreHost.mm').read_text()
start = host.index('- (void)requestDevelopmentCheckpoint {')
end = host.index('\n- (void)restoreDevelopmentCheckpoint', start)
method = host[start:end]
assert method.count('State::SaveAs(') == 1
assert method.index('#if TARGET_OS_SIMULATOR') < method.index('State::SaveAs(') < method.index('#endif')
for guard in ('GalaxyPadDevCheckpoints', '_session->stopping', 'Core::State::Running',
              'Core::State::Paused', 'existing.count >= 8', 'now - lastRequest < 30',
              '2LL * 1024 * 1024 * 1024', 'fileExistsAtPath:file.path'):
    assert method.index(guard) < method.index('State::SaveAs(')
assert 'NSUUID.UUID.UUIDString' in method
assert '@"GalaxyPad/DevelopmentCheckpoints"' in method
assert 'State::Load' not in method and 'removeItem' not in method
assert 'completion not yet verified' in method
overlay = (root / 'apple/ios/GalaxyPadGameOverlay.mm').read_text()
block = overlay[overlay.index('if ([NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevCheckpoints"]'):]
assert block.index('gameOverlayRequestsDevelopmentCheckpoint:') < block.index('Save Development Checkpoint')
assert 'gameOverlayRequestsDevelopmentCheckpoint:' in (root / 'apple/ios/main.mm').read_text()
restore = host[end:host.index('\n- (BOOL)startWithGameRoot:', end)]
assert restore.index('GalaxyPadCheckpointIdentityMatches') < restore.index('State::LoadAsWithoutRetainingUndo(')
assert restore.index('NSFileTypeRegular') < restore.index('State::LoadAsWithoutRetainingUndo(')
assert restore.index('512ULL*1024*1024') < restore.index('State::LoadAsWithoutRetainingUndo(')
with tempfile.TemporaryDirectory(prefix='galaxypad-checkpoint-test-') as temporary:
    folder = Path(temporary)
    fixture = folder / 'data'
    fixture.write_bytes(b'abc')
    code = r'''
#import "GalaxyPadDevelopmentCheckpoint.h"
#include <cassert>
int main(int argc, char** argv) { @autoreleasepool {
  NSDictionary* identity=@{@"app":@"a", @"module":@"b", @"nandSave":@"c"};
  assert(GalaxyPadCheckpointIdentityMatches(identity,identity));
  assert(!GalaxyPadCheckpointIdentityMatches(nil,identity));
  assert(!GalaxyPadCheckpointIdentityMatches(identity,nil));
  for (NSString* key in identity) {
    NSMutableDictionary* other=[identity mutableCopy]; other[key]=@"changed";
    assert(!GalaxyPadCheckpointIdentityMatches(identity,other));
  }
  NSString* valid=@"f1888152-2628-4196-bdbb-c7d8e8ea4c3a.sav";
  assert(GalaxyPadCheckpointFilenameValid(valid));
  assert(!GalaxyPadCheckpointFilenameValid(nil));
  for (NSString* bad in @[@"../state.sav",@"/tmp/a.sav",@"abc.sav",@"",@"a.tmp",
                          [@"../" stringByAppendingString:valid]])
    assert(!GalaxyPadCheckpointFilenameValid(bad));
  NSString* path=[NSString stringWithUTF8String:argv[1]];
  assert([GalaxyPadCheckpointHash(path) isEqualToString:
    @"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"]);
  assert(GalaxyPadCheckpointHash([path stringByAppendingString:@".missing"])==nil);
} }
'''
    source = folder / 'test.mm'
    source.write_text(code)
    binary = folder / 'test'
    subprocess.run(['clang++', '-std=c++20', '-fobjc-arc', '-Wno-deprecated-declarations',
                    '-fsanitize=address,undefined', '-I'+str(root/'apple/ios'),
                    '-framework', 'Foundation', str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary), str(fixture)], check=True, timeout=10)
print('Development checkpoint source gates, unique path and non-destructive request contract pass; not runtime save proof')
