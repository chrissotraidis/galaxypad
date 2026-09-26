#!/usr/bin/env python3
"""Prepare only: immutable-source copies, VFS overlay and isolated build commands.

No compilation, archive copying, signing, installation or runtime actions.
"""
from pathlib import Path
import hashlib
import json
import shlex
import argparse
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=root/'generated/experiments/efb-batching-20260913')
parser.add_argument('--batch',action='store_true',help='Include the default-off direct-copy encoder prototype')
options=parser.parse_args()
out=options.output.resolve()
out.mkdir(parents=True,exist_ok=True)
corebase=root/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912'
hostbase=root/'generated/build/ios-simulator-settings-perf13-final-20260913'
core=root/'ref/ModernGekko/vendor/dolphin/Source/Core'
probe=Path(__file__).with_name('EfbBatchProbe.h').resolve()
include='#include "'+str(probe)+'"\n'
sources={name:core/relative for name,relative in {
 'FramebufferManager.cpp':'VideoCommon/FramebufferManager.cpp',
 'MTLTexture.mm':'VideoBackends/Metal/MTLTexture.mm',
 'MTLStateTracker.mm':'VideoBackends/Metal/MTLStateTracker.mm'}.items()}
sources['GalaxyPadCoreHost.mm']=root/'apple/ios/GalaxyPadCoreHost.mm'
texts={name:path.read_text() for name,path in sources.items()}
def replace(name,old,new,count=1):
    assert texts[name].count(old)==count,(name,old,texts[name].count(old),count)
    texts[name]=texts[name].replace(old,new)
name='FramebufferManager.cpp'
replace(name,'void FramebufferManager::RefreshPeekCache()\n{',
        'void FramebufferManager::RefreshPeekCache()\n{\n  galaxypad::efb_batch_probe::RefreshScope efb_probe_refresh;')
replace(name,'void FramebufferManager::PopulateEFBCache(bool depth, u32 tile_index, bool async)\n{',
        'void FramebufferManager::PopulateEFBCache(bool depth, u32 tile_index, bool async)\n{\n  galaxypad::efb_batch_probe::PopulateScope efb_probe_populate;')
replace(name,'  if (GetEFBScale() != 1 || force_intermediate_copy)',
        '  efb_probe_populate.setIntermediate(GetEFBScale() != 1 || force_intermediate_copy);\n  if (GetEFBScale() != 1 || force_intermediate_copy)')
name='MTLTexture.mm'
replace(name,'    id<MTLBlitCommandEncoder> download_encoder = [m_wait_buffer blitCommandEncoder];',
'''    id<MTLBlitCommandEncoder> download_encoder = [m_wait_buffer blitCommandEncoder];
    galaxypad::efb_batch_probe::Copy(
      reinterpret_cast<std::uintptr_t>((id<MTLCommandBuffer>)m_wait_buffer),
      reinterpret_cast<std::uintptr_t>(static_cast<const Texture*>(src)->GetMTLTexture()),
      reinterpret_cast<std::uintptr_t>((id<MTLBuffer>)m_buffer));''')
replace(name,'  id<MTLBlitCommandEncoder> blit = [g_state_tracker->GetRenderCmdBuf() blitCommandEncoder];',
        '  galaxypad::efb_batch_probe::OtherWork();\n  id<MTLBlitCommandEncoder> blit = [g_state_tracker->GetRenderCmdBuf() blitCommandEncoder];')
replace(name,'    id<MTLBlitCommandEncoder> upload_encoder = [m_wait_buffer blitCommandEncoder];',
        '    galaxypad::efb_batch_probe::OtherWork();\n    id<MTLBlitCommandEncoder> upload_encoder = [m_wait_buffer blitCommandEncoder];')
name='MTLStateTracker.mm'
for signature in [
 'id<MTLBlitCommandEncoder> Metal::StateTracker::GetUploadEncoder()',
 'id<MTLBlitCommandEncoder> Metal::StateTracker::GetTextureUploadEncoder()',
 'void Metal::StateTracker::BeginRenderPass(MTLRenderPassDescriptor* descriptor)',
 'void Metal::StateTracker::BeginComputePass()',
 'void Metal::StateTracker::FlushEncoders()']:
    replace(name,signature+'\n{',signature+'\n{\n  galaxypad::efb_batch_probe::OtherWork();')
replace(name,'  id<MTLRenderCommandEncoder> enc =\n      [GetRenderCmdBuf() renderCommandEncoderWithDescriptor:m_resolve_pass_desc];',
        '  galaxypad::efb_batch_probe::OtherWork();\n  id<MTLRenderCommandEncoder> enc =\n      [GetRenderCmdBuf() renderCommandEncoderWithDescriptor:m_resolve_pass_desc];')
name='GalaxyPadCoreHost.mm'
replace(name,'  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];',
'''  const bool efbBatchProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevEfbBatchProbe"];
  galaxypad::efb_batch_probe::enabled.store(efbBatchProbe,std::memory_order_relaxed);
  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];''')
replace(name,'          // Read presenter geometry on its rendering thread, not from UIKit.',
'''#if TARGET_OS_SIMULATOR
          auto efbBatchProbeHook=GetVideoEvents().vi_end_field_event.Register(
            [efbBatchProbe,fields=0u,records=0u]() mutable {
              if(!efbBatchProbe || ++fields%120 || records>=128 || !Core::IsCPUThread()) return;
              auto snapshot=galaxypad::efb_batch_probe::Read();
              if(!snapshot) return;
              ++records;
              const auto& c=*snapshot;
              GalaxyPadLogPerformanceWindow(@[[NSString stringWithFormat:
                @"efb_batch_probe record=%u field=%u refresh=%llu active=%llu refreshCopies=%llu demandCopies=%llu direct=%llu intermediate=%llu blitEncoders=%llu contiguousPairs=%llu sameResourcePairs=%llu multiCopyRefresh=%llu maxCopies=%llu maxRun=%llu",
                records,fields,(unsigned long long)c[0],(unsigned long long)c[1],
                (unsigned long long)c[2],(unsigned long long)c[3],(unsigned long long)c[4],
                (unsigned long long)c[5],(unsigned long long)c[6],(unsigned long long)c[7],
                (unsigned long long)c[8],(unsigned long long)c[9],(unsigned long long)c[10],
                (unsigned long long)c[11]]]);
            });
#endif
          // Read presenter geometry on its rendering thread, not from UIKit.''')
extra_inputs={}
if options.batch:
    batch_header=Path(__file__).with_name('MetalEfbBatch.h').resolve()
    batch_impl=Path(__file__).with_name('MetalEfbBatchImpl.inc').resolve()
    include+='#include "'+str(batch_header)+'"\n'
    for path in [batch_header,batch_impl]:
        extra_inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    name='FramebufferManager.cpp'
    replace(name,'  bool flush_command_buffer = false;',
            '  galaxypad::efb_direct_batch::RefreshScope efb_direct_refresh;\n  bool flush_command_buffer = false;')
    replace(name,'  galaxypad::efb_batch_probe::PopulateScope efb_probe_populate;',
            '  galaxypad::efb_batch_probe::PopulateScope efb_probe_populate;\n  galaxypad::efb_direct_batch::PopulateScope efb_direct_populate;')
    replace(name,'  efb_probe_populate.setIntermediate(GetEFBScale() != 1 || force_intermediate_copy);',
            '  efb_probe_populate.setIntermediate(GetEFBScale() != 1 || force_intermediate_copy);\n  efb_direct_populate.setIntermediate(GetEFBScale() != 1 || force_intermediate_copy);')
    name='MTLStateTracker.mm'
    for signature in ['void Metal::StateTracker::EndRenderPass()',
                      'void Metal::StateTracker::FlushEncoders()',
                      'id<MTLBlitCommandEncoder> Metal::StateTracker::GetUploadEncoder()',
                      'id<MTLBlitCommandEncoder> Metal::StateTracker::GetTextureUploadEncoder()']:
        replace(name,signature+'\n{',signature+'\n{\n  galaxypad::efb_direct_batch::EndMetalBatch();')
    name='MTLTexture.mm'
    replace(name,'#include "VideoBackends/Metal/MTLStateTracker.h"',
            '#include "VideoBackends/Metal/MTLStateTracker.h"\n#include "'+str(batch_impl)+'"')
    replace(name,'''    g_state_tracker->EndRenderPass();
    m_wait_buffer = MRCRetain(g_state_tracker->GetRenderCmdBuf());
    id<MTLBlitCommandEncoder> download_encoder = [m_wait_buffer blitCommandEncoder];''',
'''    const bool direct_batch=galaxypad::efb_direct_batch::Eligible();
    // Generic EndRenderPass closes every live batch for all native callers.
    // Only this exact continuation path can preserve the existing blit encoder.
    if(!direct_batch || !galaxypad::efb_direct_batch::HasMetalBatch())
      g_state_tracker->EndRenderPass();
    m_wait_buffer = MRCRetain(g_state_tracker->GetRenderCmdBuf());
    bool encoder_created=true;
    id<MTLBlitCommandEncoder> download_encoder=direct_batch ?
      galaxypad::efb_direct_batch::AcquireMetalBatch(m_wait_buffer,
        static_cast<const Texture*>(src)->GetMTLTexture(),m_buffer,&encoder_created) :
      [m_wait_buffer blitCommandEncoder];''')
    replace(name,'      reinterpret_cast<std::uintptr_t>((id<MTLBuffer>)m_buffer));',
            '      reinterpret_cast<std::uintptr_t>((id<MTLBuffer>)m_buffer),encoder_created);')
    replace(name,'    [download_encoder endEncoding];','    if(!direct_batch) [download_encoder endEncoding];')
    name='GalaxyPadCoreHost.mm'
    replace(name,'  const bool efbBatchProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevEfbBatchProbe"];',
'''  const bool efbDirectBatch=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevEfbDirectBatch"];
  galaxypad::efb_direct_batch::enabled.store(efbDirectBatch,std::memory_order_relaxed);
  const bool efbBatchProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevEfbBatchProbe"];''')
overlay={'version':0,'use-external-names':False,'roots':[]}
hashes={}
for name,path in sources.items():
    (out/(name+'.original')).write_text(path.read_text())
    target=out/name
    target.write_text(include+texts[name])
    overlay['roots'].append({'type':'file','name':str(path),'external-contents':str(target)})
    hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
(out/'overlay.json').write_text(json.dumps(overlay,indent=2)+'\n')
database=json.loads((corebase/'core/compile_commands.json').read_text())
hostrecipe=json.loads((hostbase/'recipe.json').read_text())
commands=[]
for name in sources:
    if name=='GalaxyPadCoreHost.mm':
        command=next(c.copy() for c in hostrecipe['compile_commands'] if str(sources[name]) in c)
        directory=str(root)
        old=command[command.index('-o')+1]
        command=[x.replace(old,str(out/(name+'.o'))) for x in command]
    else:
        item=next(c for c in database if c['file']==str(sources[name]))
        command=shlex.split(item['command']);directory=item['directory']
        command[command.index('-o')+1]=str(out/(name+'.o'))
    command+=['-ivfsoverlay',str(out/'overlay.json')]
    commands.append({'directory':directory,'argv':command})
link=hostrecipe['link'].copy()
for i,value in enumerate(link):
    if value.endswith('/objects/GalaxyPadCoreHost.mm.o'):link[i]=str(out/'GalaxyPadCoreHost.mm.o')
    elif value.endswith('/libGalaxyPadCore.a'):link[i]=str(out/'libGalaxyPadCore.a')
    elif value.startswith('-Wl,-map,'):link[i]='-Wl,-map,'+str(out/'host-link.map')
link[link.index('-o')+1]=str(out/'GalaxyPad.app/GalaxyPad')
recipe={'status':'prepared only; no compilation or runtime changes','source_hashes':hashes,
        'batch_prototype':options.batch,'extra_input_hashes':extra_inputs,
        'probe_header':str(probe),'probe_header_sha256':hashlib.sha256(probe.read_bytes()).hexdigest(),
        'core_sha256':hostrecipe['core_sha256'],'original_core':str(corebase/'libGalaxyPadCore.a'),
        'original_app':str(hostbase/'GalaxyPad.app'),'compile_commands':commands,'link':link,
        'replace_members':[name+'.o' for name in sources if name!='GalaxyPadCoreHost.mm']}
(out/'recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
print(out)
