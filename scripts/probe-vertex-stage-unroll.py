#!/usr/bin/env python3
"""Private four-stage dispatch candidate; real converters, no runtime/app mutation.

Default: complete-loop differential under ASan/UBSan. --benchmark is an isolated
CPU cost screen, not FPS acceptance. --object compiles the actual Simulator TU
with its existing compile command. Output directory must not already exist.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core'
PINS = {
    'VertexLoader': 'ece77ff1ee765eff0b1abb40fbe4bddf0e89a1b8720d754af16f1026328dfb40',
    'VertexLoader_Position': 'fd1d3ffd47af0b3c656aad19edf1aa83749e1ccc1bb03f759caf0e4fb904841b',
    'VertexLoader_Normal': 'e7117a202979aa46d5778787b2600e6de0c18e96e99415495b275cc5a5b5b085',
    'VertexLoader_TextCoord': '7267d4dbe2da6b4b55ebfcf251341143f4b69290df52641e9e132112b870d266',
    'VertexLoader_Color': '69550575bc8017b8c2b5abf458382e5995cf640fb8528b6af3c4712451cb95d0',
}
OLD = '''    for (TPipelineFunction& func : m_PipelineStages)
      func(this);'''
NEW = '''    auto* stage = m_PipelineStages.begin();
    const auto* end = m_PipelineStages.end();
    for (; end - stage >= 4; stage += 4)
    {
      stage[0](this);
      stage[1](this);
      stage[2](this);
      stage[3](this);
    }
    for (; stage != end; ++stage)
      (*stage)(this);'''

def function(source, signature):
    start = source.index(signature)
    body = source.index('{', start)
    depth = 1
    end = body + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end] + '\n'

HEADER = r'''
#pragma once
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <limits>
#include <type_traits>
#include "Common/SmallVector.h"
#include "VideoCommon/VertexLoaderUtils.h"
#define LOG_VTX()
#define LOG_NORM()
#define PRIM_LOG(...)
struct VertexLoader;
using TPipelineFunction = void (*)(VertexLoader*);
struct VertexLoader {
 float m_posScale=0.25f, m_tcScale[8]={1,0.5f,0.25f,0.125f,1,1,1,1};
 int m_tcIndex=0, m_colIndex=0;
 u8 m_curtexmtx[8]={}; int m_texmtxwrite=0, m_texmtxread=0;
 bool m_vertexSkip=false; int m_skippedVertices=0, m_remaining=0;
 struct { int stride=0; } m_native_vtx_decl;
 u64 m_numLoadedVertices=0;
 Common::SmallVector<TPipelineFunction,30> m_PipelineStages;
 int Control(const u8*,u8*,int); int Candidate(const u8*,u8*,int);
};
namespace CPArray { constexpr int Position=0, Normal=1, Color0=2, TexCoord0=4; }
struct CPState { std::array<u32,12> array_strides; };
extern CPState g_main_cp_state;
namespace VertexLoaderManager {
extern std::array<const u8*,12> cached_arraybases;
extern float position_cache[3][3], normal_cache[3], tangent_cache[3], binormal_cache[3];
extern u32 position_matrix_index_cache[3];
}
void Configure(VertexLoader&,int);
void Marker(VertexLoader*);
extern u64 trace_hash;
'''
DRIVER = r'''
#include "fixture.h"
#include <chrono>
#include <ctime>
#include <iostream>
#include <random>
#include <vector>
const u8* g_video_buffer_read_ptr;
u8* g_vertex_manager_write_ptr;
CPState g_main_cp_state;
namespace VertexLoaderManager {
std::array<const u8*,12> cached_arraybases;
float position_cache[3][3], normal_cache[3], tangent_cache[3], binormal_cache[3];
u32 position_matrix_index_cache[3];
}
u64 trace_hash;
void Marker(VertexLoader* l) { trace_hash=trace_hash*33+u64(++l->m_colIndex)+u64(l->m_remaining); }
std::array<u8,84> Caches() {
 std::array<u8,84> result{};
 memcpy(result.data(),VertexLoaderManager::position_cache,36);
 memcpy(result.data()+36,VertexLoaderManager::normal_cache,12);
 memcpy(result.data()+48,VertexLoaderManager::tangent_cache,12);
 memcpy(result.data()+60,VertexLoaderManager::binormal_cache,12);
 memcpy(result.data()+72,VertexLoaderManager::position_matrix_index_cache,12);
 return result;
}
void Reset() {
 memset(VertexLoaderManager::position_cache,0x39,36);
 memset(VertexLoaderManager::normal_cache,0x29,12);
 memset(VertexLoaderManager::tangent_cache,0x19,12);
 memset(VertexLoaderManager::binormal_cache,0x49,12);
 memset(VertexLoaderManager::position_matrix_index_cache,0x59,12); trace_hash=0;
}
u64 Hash(const std::vector<u8>& a) { u64 n=0;for(auto b:a)n=n*33+b;return n; }
int main(int argc,char**) {
 std::mt19937 rng(20260912);
 std::vector<u8> ram(65536*32),input(32768),a(65536),b(65536);
 for(auto& x:ram)x=rng();
 for(auto& x:input)x=rng();
 input[0]=input[1]=0xff; // Explicit indexed-position skip, including count=1.
 for(int i=0;i<12;++i) { VertexLoaderManager::cached_arraybases[i]=ram.data();g_main_cp_state.array_strides[i]=32; }
 int cases=0;
 for(int config=-30;config<=8;++config) {
  for(int count:{0,1,2,3,4,17,128}) for(int offset:{0,1,7}) {
   VertexLoader x{},y{};Configure(x,config);Configure(y,config);
   std::fill(a.begin(),a.end(),0xa5);b=a;
   Reset();int ra=x.Control(input.data()+offset,a.data()+offset,count);
   auto ca=Caches();auto ha=trace_hash;
   auto read=g_video_buffer_read_ptr-(input.data()+offset);auto write=g_vertex_manager_write_ptr-(a.data()+offset);
   Reset();int rb=y.Candidate(input.data()+offset,b.data()+offset,count);
   assert(ra==rb && a==b && ca==Caches() && ha==trace_hash);
   assert(read==g_video_buffer_read_ptr-(input.data()+offset));
   assert(write==g_vertex_manager_write_ptr-(b.data()+offset));
   assert(x.m_remaining==y.m_remaining && x.m_skippedVertices==y.m_skippedVertices);
   assert(x.m_vertexSkip==y.m_vertexSkip && x.m_colIndex==y.m_colIndex && x.m_tcIndex==y.m_tcIndex);
   assert(x.m_numLoadedVertices==y.m_numLoadedVertices);++cases;
  }
 }
 std::cout<<"PASS "<<cases<<" complete-loop cases: bytes, caches, cursors, skips, stage order, counters\n";
 if(argc<2)return 0;
 using Fn=int(VertexLoader::*)(const u8*,u8*,int);
 Fn funcs[]={&VertexLoader::Control,&VertexLoader::Candidate};
 std::cout<<"config,round,variant,cpu_ns_per_vertex,wall_ns_per_vertex,checksum\n";
 for(int config:{1,2,4,8}) for(int round=0;round<4;++round)for(int order=0;order<2;++order) {
  int variant=order^(round&1);VertexLoader loader{};Configure(loader,config); Reset();
  constexpr int calls=40000,count=128;u64 checksum=0;
  auto wall=std::chrono::steady_clock::now();auto cpu=std::clock();
  for(int i=0;i<calls;++i)checksum+=(loader.*funcs[variant])(input.data(),a.data(),count);
  double cn=double(std::clock()-cpu)*1e9/CLOCKS_PER_SEC/(calls*count);
  double wn=std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-wall).count()/(calls*count);
  checksum+=Hash(a)+loader.m_numLoadedVertices;
  std::cout<<config<<','<<round<<','<<variant<<','<<cn<<','<<wn<<','<<checksum<<'\n';
 }
}
'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--benchmark',action='store_true')
    p.add_argument('--object',action='store_true')
    args=p.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    sources={}
    for name,digest in PINS.items():
        data=(CORE/'VideoCommon'/f'{name}.cpp').read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:raise SystemExit(f'Source changed: {name}')
        sources[name]=data.decode()
    source=sources['VertexLoader']
    assert source.count(OLD)==1
    staged=out/'VertexLoader.cpp';staged.write_text(source.replace(OLD,NEW))
    original=function(source,'int VertexLoader::RunVertices(')
    loops=original.replace('::RunVertices','::Control')+original.replace(OLD,NEW).replace('::RunVertices','::Candidate')
    (out/'fixture.h').write_text(HEADER)
    (out/'loops.cpp').write_text('#include "fixture.h"\n'+loops)
    callbacks=''
    for name,begin,end in [('Position','template <typename T>\nconstexpr float PosScale','using ComponentCountRow'),('Normal','template <typename T>\nconstexpr float FracAdjust','using Common::EnumMap'),('TextCoord','void TexCoord_Read_Dummy','using ComponentCountRow')]:
        s=sources['VertexLoader_'+name];callbacks+=s[s.index(begin):s.index(end)]
    color=sources['VertexLoader_Color']
    for signature in ['void SetCol(','u32 Read32(','template <typename I>\nvoid Color_ReadIndex_32b_8888(']:callbacks+=function(color,signature)
    callbacks+=function(source,'static void SkipVertex(')
    callbacks+='''\nvoid Configure(VertexLoader& l,int config) {
 if(config<=0) {for(int i=0;i<-config;++i)l.m_PipelineStages.push_back(Marker);return;}
 l.m_PipelineStages.push_back(Pos_ReadIndex<u16,s16,3>);
 l.m_PipelineStages.push_back(Normal_ReadIndex<u16,s16,1>);
 l.m_PipelineStages.push_back(Color_ReadIndex_32b_8888<u16>);
 for(int i=0;i<config;++i)l.m_PipelineStages.push_back(TexCoord_ReadIndex<u16,s16,2>);
 l.m_PipelineStages.push_back(SkipVertex);l.m_native_vtx_decl.stride=28+config*8;
}\n'''
    (out/'callbacks.cpp').write_text('#include "fixture.h"\n'+callbacks)
    (out/'driver.cpp').write_text(DRIVER)
    flags=['clang++','-std=c++20','-O2','-fno-fast-math','-ffp-contract=off','-I'+str(CORE),'-I'+str(CORE.parents[1]/'Externals/fmt/fmt/include'),'-I'+str(out)]
    inputs=[str(out/(f+'.cpp')) for f in ['loops','callbacks','driver']]
    subprocess.run(flags+['-fsanitize=address,undefined']+inputs+['-o',str(out/'parity')],check=True)
    result=subprocess.check_output([str(out/'parity')],text=True,timeout=30)
    (out/'parity.txt').write_text(result);print(result,end='')
    if args.benchmark:
        subprocess.run(flags+inputs+['-o',str(out/'benchmark')],check=True)
        result=subprocess.check_output([str(out/'benchmark'),'benchmark'],text=True,timeout=60)
        (out/'benchmark.csv').write_text(result);print(result,end='')
    if args.object:
        entries=json.loads((ROOT/'generated/build/ios-simulator-core/compile_commands.json').read_text())
        entry,=[e for e in entries if e['file'].endswith('/VertexLoader.cpp')]
        for variant,path in [('control',CORE/'VideoCommon/VertexLoader.cpp'),('candidate',staged)]:
            argv=shlex.split(entry['command']);argv[argv.index('-c')+1]=str(path);argv[argv.index('-o')+1]=str(out/(variant+'.o'))
            subprocess.run(argv,cwd=entry['directory'],check=True,timeout=60)
    (out/'sources.json').write_text(json.dumps(PINS,indent=2)+'\n')

if __name__=='__main__':main()
