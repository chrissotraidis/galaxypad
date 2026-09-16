#!/usr/bin/env python3
"""Differential test and optional host benchmark of the opt-in indexed batch decoder.

Real converter bodies and candidate matcher/kernel; synthetic format-resolution
shims select the real callbacks. This does not prove live format coverage or FPS.
"""
import argparse
import importlib.util,json,subprocess,hashlib
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--benchmark',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('fixture',root/'scripts/probe-vertex-stage-unroll.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
s=(m.CORE/'VideoCommon/VertexLoader.cpp').read_text();fun=m.function(s,'int VertexLoader::RunVertices(')
start=fun.index('#if GALAXYPAD_INDEXED_VERTEX_BATCH');end=fun.index('#endif',start)+len('#endif')
control=fun[:start]+fun[end:]
header='#include <cstdio>\n'+m.HEADER+'''
enum class VertexComponentFormat { Index16 };
enum class ComponentFormat { Short };
enum class CoordComponentCount { XYZ };
enum class NormalComponentCount { N };
enum class TexComponentCount { ST };
enum class ColorFormat { RGBA8888 };
struct VertexLoader_Position {static TPipelineFunction GetFunction(VertexComponentFormat,ComponentFormat,CoordComponentCount);};
struct VertexLoader_Normal {static TPipelineFunction GetFunction(VertexComponentFormat,ComponentFormat,NormalComponentCount,bool);};
struct VertexLoader_Color {static TPipelineFunction GetFunction(VertexComponentFormat,ColorFormat);};
struct VertexLoader_TextCoord {static TPipelineFunction GetFunction(VertexComponentFormat,ComponentFormat,TexComponentCount);};
void PosMtx_ReadDirect_UByte(VertexLoader*);
void SkipVertex(VertexLoader*);
'''
(out/'fixture.h').write_text(header)
(out/'loops.cpp').write_text('#include "fixture.h"\n#include "VideoCommon/VertexLoaderIndexedBatch.h"\n'+control.replace('::RunVertices','::Control')+fun.replace('::RunVertices','::Candidate'))
callbacks=''
for name,begin,end in [('Position','template <typename T>\nconstexpr float PosScale','using ComponentCountRow'),('Normal','template <typename T>\nconstexpr float FracAdjust','using Common::EnumMap'),('TextCoord','void TexCoord_Read_Dummy','using ComponentCountRow')]:
 text=(m.CORE/f'VideoCommon/VertexLoader_{name}.cpp').read_text();callbacks+=text[text.index(begin):text.index(end)]
color=(m.CORE/'VideoCommon/VertexLoader_Color.cpp').read_text()
for sig in ['void SetCol(','u32 Read32(','template <typename I>\nvoid Color_ReadIndex_32b_8888(']:callbacks+=m.function(color,sig)
for sig in ['static void SkipVertex(','static void PosMtx_ReadDirect_UByte(']:callbacks+=m.function(s,sig).replace('static void','void')
callbacks+='''
TPipelineFunction VertexLoader_Position::GetFunction(VertexComponentFormat,ComponentFormat,CoordComponentCount){return Pos_ReadIndex<u16,s16,3>;}
TPipelineFunction VertexLoader_Normal::GetFunction(VertexComponentFormat,ComponentFormat,NormalComponentCount,bool){return Normal_ReadIndex<u16,s16,1>;}
TPipelineFunction VertexLoader_Color::GetFunction(VertexComponentFormat,ColorFormat){return Color_ReadIndex_32b_8888<u16>;}
TPipelineFunction VertexLoader_TextCoord::GetFunction(VertexComponentFormat,ComponentFormat,TexComponentCount){return TexCoord_ReadIndex<u16,s16,2>;}
void Configure(VertexLoader& l,int config){
 if(config<0){for(int i=0;i<-config;++i)l.m_PipelineStages.push_back(Marker);return;}
 int perturb=config>=36?config-36:-1; if(perturb>=0)config=6;
 bool matrix=config&1,color=config&2;int tc=config/4;
 if(matrix)l.m_PipelineStages.push_back(PosMtx_ReadDirect_UByte);
 l.m_PipelineStages.push_back(Pos_ReadIndex<u16,s16,3>);
 l.m_PipelineStages.push_back(Normal_ReadIndex<u16,s16,1>);
 if(color)l.m_PipelineStages.push_back(Color_ReadIndex_32b_8888<u16>);
 for(int i=0;i<tc;++i)l.m_PipelineStages.push_back(TexCoord_ReadIndex<u16,s16,2>);
 l.m_PipelineStages.push_back(SkipVertex);l.m_native_vtx_decl.stride=24+4*matrix+4*color+8*tc;
 if(perturb>=0) { if(perturb&1)l.m_PipelineStages.push_back(Marker);else l.m_PipelineStages[0]=Pos_ReadIndex<u8,s16,3>; }
}
'''
(out/'callbacks.cpp').write_text('#include "fixture.h"\n'+callbacks)
driver=m.DRIVER.replace('config<=8','config<=39').replace('for(int config:{1,2,4,8})','for(int config:{6,7,10,11,18,19,34,35})')
# Randomize each batch and explicitly skip every combination of its final records.
driver=driver.replace('for(int offset:{0,1,7}) {','for(int offset:{0,1,7}) for(int mask=0;mask<8;++mask) {\n for(auto& v:input)v=rng();\n if(config>=0) {int stride=(config&1)+4+((config&2)?2:0)+2*(config/4);for(int i=0;i<std::min(count,3);++i) if(mask&(1<<i)){int at=offset+(count-1-i)*stride+(config&1);input[at]=input[at+1]=255;}}')
(out/'driver.cpp').write_text(driver)
flags=['clang++','-std=c++20','-O2','-fno-fast-math','-ffp-contract=off','-DGALAXYPAD_INDEXED_VERTEX_BATCH=1','-I'+str(m.CORE),'-I'+str(root/'ref/ModernGekko/vendor/fmt/fmt/include'),'-I'+str(out)]
inputs=[str(out/(f+'.cpp')) for f in ['loops','callbacks','driver']]
for sanitized in ([True,False] if args.benchmark else [True]):
 binary=out/('parity' if sanitized else 'benchmark');subprocess.run(flags+(['-fsanitize=address,undefined'] if sanitized else [])+inputs+['-o',str(binary)],check=True)
 result=subprocess.check_output([str(binary)]+([] if sanitized else ['benchmark']),text=True);(out/(binary.name+'.txt')).write_text(result);print(result)

(out/'source-hashes.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [m.CORE/'VideoCommon'/name for name in ['VertexLoader.cpp','VertexLoaderIndexedBatch.h','VertexLoader_Position.cpp','VertexLoader_Normal.cpp','VertexLoader_TextCoord.cpp','VertexLoader_Color.cpp']]},indent=2)+'\n')
