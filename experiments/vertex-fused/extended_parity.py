import argparse,pathlib,subprocess,json
parser=argparse.ArgumentParser();parser.add_argument('--experiment',type=pathlib.Path,required=True);p=parser.parse_args().experiment.resolve();r=pathlib.Path(__file__).resolve().parents[2];core=r/'ref/ModernGekko/vendor/dolphin/Source/Core'
s=(p/'driver.cpp').read_text();s=s.replace('for(int config=-30;config<=8;++config)', 'for(int stride:{1,7,14,31,32}) for(int guard=0;guard<6;++guard) for(int config=1;config<=2;++config)')
s=s.replace('x.m_VtxAttr.g0.Hex=y.m_VtxAttr.g0.Hex=(x.m_VtxAttr.g0.Hex & ~((31u<<4)|(31u<<25)))|(u32(pf)<<4)|(u32(tf)<<25);', '''x.m_VtxAttr.g0.Hex=y.m_VtxAttr.g0.Hex=(x.m_VtxAttr.g0.Hex & ~((31u<<4)|(31u<<25)))|(u32(pf)<<4)|(u32(tf)<<25);
   for(int i=0;i<12;++i) {VertexLoaderManager::cached_arraybases[i]=ram.data()+128*i;g_main_cp_state.array_strides[i]=stride;}
   if(guard) {
    if(guard==1)x.m_VtxDesc.low.Hex=y.m_VtxDesc.low.Hex=x.m_VtxDesc.low.Hex^1;
    if(guard==2)x.m_VtxDesc.high.Hex=y.m_VtxDesc.high.Hex=7;
    if(guard==3)x.m_VtxAttr.g0.Hex=y.m_VtxAttr.g0.Hex=x.m_VtxAttr.g0.Hex^2;
    if(guard==4)x.m_VtxAttr.g1.Hex=y.m_VtxAttr.g1.Hex=x.m_VtxAttr.g1.Hex^1;
    if(guard==5)x.m_VtxAttr.g2.Hex=y.m_VtxAttr.g2.Hex=x.m_VtxAttr.g2.Hex^1;
    x.m_PipelineStages.push_back(Marker);y.m_PipelineStages.push_back(Marker);
   }''')
# RAM ends beyond all array-base offsets plus the largest legal u16 indexed element.
s=s.replace('ram(65536*32)','ram(65536*32+4096)')
(p/'driver-extended.cpp').write_text(s)
flags=['clang++','-std=c++20','-O3','-fno-fast-math','-ffp-contract=off','-I'+str(core),'-I'+str(core.parents[1]/'Externals/fmt/fmt/include'),'-I'+str(p),'-fsanitize=address,undefined']
for name,extra in [('extended-full',[]),('extended-unaligned',['-fno-sanitize=alignment'])]:
 subprocess.run(flags+extra+[str(p/'loops.cpp'),str(p/'driver-extended.cpp'),'-o',str(p/name)],check=True)
 result=subprocess.run([str(p/name)],text=True,capture_output=True);(p/(name+'.txt')).write_text(result.stdout+result.stderr);print(name, 'ALIGNMENT FINDINGS (not a clean UBSan pass)' if result.stderr else 'CLEAN', result.returncode,result.stdout.strip(),'stderr lines',len(result.stderr.splitlines()))
 if result.returncode or (name=='extended-unaligned' and result.stderr):raise SystemExit('Parity/sanitizer check failed; inspect the saved report')
