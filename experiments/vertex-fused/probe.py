#!/usr/bin/env python3
"""Source-extracted fused-converter parity and isolated CPU screen; no shared-core edits."""
import argparse,hashlib,importlib.util,pathlib,subprocess,json,shlex
root=pathlib.Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('probe',root/'scripts/probe-vertex-stage-unroll.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=pathlib.Path,required=True);args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
sources={n:(p.CORE/'VideoCommon'/f'{n}.cpp').read_text() for n in p.PINS}
for name,digest in p.PINS.items():
 assert hashlib.sha256(sources[name].encode()).hexdigest()==digest, f'Source changed: {name}'
(out/'source-pins.json').write_text(json.dumps(p.PINS,indent=2))
source=sources['VertexLoader'];callbacks=''
for name,begin,end in [('Position','template <typename T>\nconstexpr float PosScale','using ComponentCountRow'),('Normal','template <typename T>\nconstexpr float FracAdjust','using Common::EnumMap'),('TextCoord','void TexCoord_Read_Dummy','using ComponentCountRow')]:
 s=sources['VertexLoader_'+name];callbacks+=s[s.index(begin):s.index(end)]
for sig in ['void SetCol(','u32 Read32(','template <typename I>\nvoid Color_ReadIndex_32b_8888(']:callbacks+=p.function(sources['VertexLoader_Color'],sig)
fused='''    if (fused) {
      GalaxyPadAOT::Pos_ReadIndex<u16,s16,3>(this);
      GalaxyPadAOT::Normal_ReadIndex<u16,s16,1>(this);
      GalaxyPadAOT::Color_ReadIndex_32b_8888<u16>(this);
      GalaxyPadAOT::TexCoord_ReadIndex<u16,s16,2>(this);
      SkipVertex(this);
    } else {
'''+p.OLD+'''\n    }'''
guard='''  const bool fused = m_VtxDesc.low.Hex == 0x00007e00 && m_VtxDesc.high.Hex == 3 &&
    (m_VtxAttr.g0.Hex & ~((31u << 4) | (31u << 25))) == 0x40f76c07 &&
    m_VtxAttr.g1.Hex == 0xc8241209 && m_VtxAttr.g2.Hex == 0x04824120;
'''
assert hex(1089956871)=='0x40f76c07'
original=p.function(source,'int VertexLoader::RunVertices(')
candidate=original.replace('  g_vertex_manager_write_ptr = dst;',guard+'  g_vertex_manager_write_ptr = dst;').replace(p.OLD,fused)
callbacks=callbacks.replace('  LOG_NORM();', '')
production=source.replace('int VertexLoader::RunVertices(', 'namespace GalaxyPadAOT {\n'+callbacks+'}\n\nint VertexLoader::RunVertices(').replace(original,candidate)
(out/'VertexLoader.cpp').write_text(production)
header=p.HEADER.replace(' int Control(', ' struct Word {u32 Hex=0;}; struct { Word low,high; } m_VtxDesc; struct {Word g0,g1,g2;} m_VtxAttr;\n int Control(')
(out/'fixture.h').write_text(header)
configure='''void Configure(VertexLoader& l,int config) {
 if(config<=0) {for(int i=0;i<-config;++i)l.m_PipelineStages.push_back(Marker);return;}
 l.m_VtxDesc.low.Hex=config==1?0x7e00:0; l.m_VtxDesc.high.Hex=3; l.m_VtxAttr.g0.Hex=0x54f76c27; l.m_VtxAttr.g1.Hex=0xc8241209; l.m_VtxAttr.g2.Hex=0x04824120;
 l.m_PipelineStages.push_back(GalaxyPadAOT::Pos_ReadIndex<u16,s16,3>);
 l.m_PipelineStages.push_back(GalaxyPadAOT::Normal_ReadIndex<u16,s16,1>);
 l.m_PipelineStages.push_back(GalaxyPadAOT::Color_ReadIndex_32b_8888<u16>);
 for(int i=0;i<config;++i)l.m_PipelineStages.push_back(GalaxyPadAOT::TexCoord_ReadIndex<u16,s16,2>);
 l.m_PipelineStages.push_back(SkipVertex);l.m_native_vtx_decl.stride=28+config*8;
}\n'''
loops=original.replace('::RunVertices','::Control')+candidate.replace('::RunVertices','::Candidate')
(out/'loops.cpp').write_text('#include "fixture.h"\nnamespace GalaxyPadAOT {\n'+callbacks+'}\n'+p.function(source,'static void SkipVertex(')+configure+loops)
driver=p.DRIVER.replace('for(int count:{0,1,2,3,4,17,128})', 'for(int pf:{0,2,16,31}) for(int tf:{0,10,16,31}) for(int count:{0,1,2,3,4,17,128})').replace('std::fill(a.begin()', '''x.m_VtxAttr.g0.Hex=y.m_VtxAttr.g0.Hex=(x.m_VtxAttr.g0.Hex & ~((31u<<4)|(31u<<25)))|(u32(pf)<<4)|(u32(tf)<<25);
   x.m_posScale=y.m_posScale=1.0f/float(1u<<pf);x.m_tcScale[0]=y.m_tcScale[0]=1.0f/float(1u<<tf);
   std::fill(a.begin()''')
(out/'driver.cpp').write_text(driver.replace('for(int config:{1,2,4,8})','for(int config:{1})').replace('constexpr int calls=40000,count=128','constexpr int calls=400000,count=5'))
flags=['clang++','-std=c++20','-O3','-fno-fast-math','-ffp-contract=off','-I'+str(p.CORE),'-I'+str(p.CORE.parents[1]/'Externals/fmt/fmt/include'),'-I'+str(out)]
inputs=[str(out/(n+'.cpp')) for n in ['loops','driver']]
for name,extra,argv in [('parity',['-fsanitize=address,undefined'],[]),('benchmark',[],['benchmark'])]:
 subprocess.run(flags+extra+inputs+['-o',str(out/name)],check=True)
 result=subprocess.check_output([str(out/name)]+argv,text=True);(out/(name+'.txt')).write_text(result);print(result)
a=root/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912'
rows=[shlex.split(line) for line in subprocess.check_output(['ninja','-C',str(a/'core'),'-t','commands'],text=True).splitlines()]
cmd=next(c for c in rows if '-c' in c and c[c.index('-c')+1]==str(p.CORE/'VideoCommon/VertexLoader.cpp'))
cmd[cmd.index('-c')+1]=str(out/'VertexLoader.cpp')
for flag in ['-o','-MT','-MF']:cmd[cmd.index(flag)+1]=str(out/'candidate.o')+('.d' if flag=='-MF' else '')
subprocess.run(cmd,cwd=a/'core',check=True)
(out/'compile.json').write_text(json.dumps(cmd,indent=2))
