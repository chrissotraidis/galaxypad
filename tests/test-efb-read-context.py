"""Exercise proposed live-AOT diagnostic scope without changing product state."""
from pathlib import Path
import os
import hashlib
import subprocess
import tempfile
from efb_source import without_dispatch_overlay

root = Path(__file__).resolve().parents[1]
header = root/'patches/experiments/efb-read-context.h'
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert bootstrap.index('apply --reverse "$efb_context_patch"') < bootstrap.index('apply --reverse "$audio_events_patch"')
assert bootstrap.index('apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$efb_context_patch"') > bootstrap.index('apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$audio_events_patch"')
scope = bootstrap.split('verify_patch_scope "$ref/ModernGekko/vendor/dolphin" "DolRecomp"', 1)[1]
assert '"$efb_context_patch"' in scope.split('cntlzw_patch=', 1)[0]
program = r'''
#include "context.h"
#include <cassert>
#include <thread>
#include <type_traits>
using namespace GalaxyPadDiagnostics;
EFBReadContext FromOtherTU();
void Check(unsigned pc, unsigned lr) {
  auto value = CurrentEFBReadContext();
  auto other = FromOtherTU();
  assert(value.pc == pc && value.lr == lr);
  assert(other.pc == pc && other.lr == lr);
}
void EarlyReturn() { ScopedEFBReadContext scope(0x80000004, 0x80000008); }
int main() {
  static_assert(!std::is_copy_constructible_v<ScopedEFBReadContext>);
  static_assert(!std::is_move_constructible_v<ScopedEFBReadContext>);
  const bool enabled = IsEFBReadContextEnabled();
  Check(0, 0);
  {
    ScopedEFBReadContext outer(0x80400000, 0x80300000);
    auto check_outer = [&] { Check(enabled ? 0x80400000 : 0, enabled ? 0x80300000 : 0); };
    check_outer();
    {
      ScopedEFBReadContext nested(0x80100000, 0x80200000);
      Check(enabled ? 0x80100000 : 0, enabled ? 0x80200000 : 0);
    }
    check_outer();
    EarlyReturn();
    check_outer();
    try {
      ScopedEFBReadContext throwing(0x80500000, 0x80600000);
      throw 7;
    } catch (int) {}
    check_outer();
    std::thread other([&] {
      Check(0, 0);
      { ScopedEFBReadContext scope(3, 4); Check(enabled ? 3 : 0, enabled ? 4 : 0); }
      Check(0, 0);
    });
    other.join();
    check_outer();
  }
  Check(0, 0);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-efb-context-') as directory:
    folder = Path(directory)
    vendor = root/'ref/ModernGekko/vendor/dolphin'
    originals = {}
    checkouts = {}
    raw_checkouts = {}
    for name, pin in [
        ('Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp', 'd31ca92693854811b7da47c5d40efb9bdb2347e50a09337ca9be1f40223a63a2'),
        ('Source/Core/VideoCommon/EFBInterface.cpp', '661ffe6c2b64b12090d0d181c279ec7d12e53cce309822e481f22796dc132a77'),
    ]:
        checkout = (vendor/name).read_bytes()
        raw_checkouts[name] = checkout
        if name.endswith('StaticRecompCore_Hooks.cpp'):
            # Independently tested opt-in census, added after this pinned EFB
            # overlay. Remove only its exact known statement for this oracle;
            # the original full-file hashes below still reject other changes.
            census = (b'  if (core->m_fallback_histogram)\n'
                      b'    core->m_fallback_histogram->Record(cia, galaxypad::diagnostics::FallbackPath::InstructionHook);\n')
            assert checkout.count(census) <= 1
            checkout = checkout.replace(census, b'')
        if name.endswith('EFBInterface.cpp'):
            checkout = without_dispatch_overlay(checkout)
        checkouts[name] = checkout
        original = checkout.replace(b'#include "Common/GalaxyPadEFBReadContext.h"\n', b'')
        original = original.replace(b'  const GalaxyPadDiagnostics::ScopedEFBReadContext read_context(cpu->pc, cpu->lr);\n', b'')
        original = original.replace(b'      GalaxyPadDiagnostics::CurrentEFBReadContext().pc,\n      GalaxyPadDiagnostics::CurrentEFBReadContext().lr);', b'      Core::System::GetInstance().GetPPCState().pc,\n      Core::System::GetInstance().GetPPCState().spr[SPR_LR]);')
        assert hashlib.sha256(original).hexdigest() == pin
        originals[name] = original
        target = folder/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original)
    patch = root/'patches/experiments/efb-live-read-context.patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == '4d5782faa59f0dc77bdc31c3bef75c2e8215088b427a308337bbfe21d410b775'
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=folder, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=folder, check=True)
    forms = []
    for name, original in originals.items():
        assert checkouts[name] in (original, (folder/name).read_bytes()), 'unknown or partial overlay'
        forms.append(checkouts[name] != original)
    for name, pin in [
        ('Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp', '4a6d2d01290bf5d74319a799eec473f1780adafabb2cd9995afeb50dfb27fc30'),
        ('Source/Core/VideoCommon/EFBInterface.cpp', '9164b11a36e898f4e2ee479b975c751deb2752f2b27047d610feb0290197405f'),
    ]:
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == pin
    assert len(set(forms)) == 1, 'mixed source overlay'
    installed_header = folder/'Source/Core/Common/GalaxyPadEFBReadContext.h'
    assert installed_header.read_bytes() == header.read_bytes()
    live_header = vendor/'Source/Core/Common/GalaxyPadEFBReadContext.h'
    assert live_header.exists() == forms[0]
    if live_header.exists():
        assert live_header.read_bytes() == header.read_bytes()
    hooks = (folder/'Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp').read_text()
    assert hooks.count('ScopedEFBReadContext read_context(cpu->pc, cpu->lr);') == 2
    efb = (folder/'Source/Core/VideoCommon/EFBInterface.cpp').read_text()
    assert efb.count('CurrentEFBReadContext().pc,') == 2
    assert efb.count('CurrentEFBReadContext().lr);') == 2
    (folder/'context.h').write_bytes(installed_header.read_bytes())
    (folder/'main.cpp').write_text(program)
    (folder/'other.cpp').write_text('#include "context.h"\nGalaxyPadDiagnostics::EFBReadContext FromOtherTU() { return GalaxyPadDiagnostics::CurrentEFBReadContext(); }\n')
    env = dict(os.environ)
    env.pop('GALAXYPAD_EFB_TRACE', None)
    for name, flags in [('sanitized', ['-O1', '-fsanitize=address,undefined']), ('optimized', ['-O2'])]:
        binary = folder/name
        subprocess.run(['clang++', '-std=c++20', *flags, '-pthread', str(folder/'main.cpp'), str(folder/'other.cpp'), '-o', str(binary)], check=True)
        for setting in (None, '', 'enabled-diagnostic.csv'):
            run_env = dict(env)
            if setting is not None:
                run_env['GALAXYPAD_EFB_TRACE'] = setting
            subprocess.run([str(binary)], env=run_env, cwd=folder, check=True)
        assert not (folder/'enabled-diagnostic.csv').exists(), 'context must not open a trace'
    subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=folder, check=True)
    assert not installed_header.exists()
    for name, original in originals.items():
        assert (folder/name).read_bytes() == original
        assert (vendor/name).read_bytes() == raw_checkouts[name]
print('EFB context nesting, exception/return restoration, cross-TU/thread isolation and opt-out pass')
