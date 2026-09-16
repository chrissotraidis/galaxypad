#!/usr/bin/env python3
"""Offline feasibility check: full indexed batches versus final-three CPU caches.

Uses the hash-gated real-converter fixture from probe-vertex-stage-unroll.py.
This checks cache side effects only, not GPU conversion, full output, culling,
memory lifetime, runtime integration or performance. No game inputs required.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).with_name('probe-vertex-stage-unroll.py')

DRIVER = r'''
int main() {
 std::mt19937 rng(20260916);
 std::vector<u8> ram(65536*32),input(32768),output(65536);
 for(auto& x:ram)x=rng();
 for(int i=0;i<12;++i) {
  VertexLoaderManager::cached_arraybases[i]=ram.data();
  g_main_cp_state.array_strides[i]=32;
 }
 int cases=0;
 for(int config=1;config<=8;++config) {
  const int inputStride=1+6+config*2; // matrix, position, normal, color, texcoords
  for(int count:{0,1,2,3,4,17,128}) for(int offset:{0,1,7})
  for(int skipMask=0;skipMask<8;++skipMask) for(int trial=0;trial<4;++trial) {
   for(auto& x:input)x=rng();
   const int tail=std::min(count,3);
   for(int i=0;i<tail;++i) if(skipMask&(1<<i)) {
    const int at=offset+(count-tail+i)*inputStride+1;
    input[at]=input[at+1]=0xff;
   }
   VertexLoader full{},suffix{};Configure(full,config);Configure(suffix,config);
   Reset();full.Control(input.data()+offset,output.data(),count);
   const auto expected=Caches();
   Reset();suffix.Control(input.data()+offset+(count-tail)*inputStride,output.data(),tail);
   assert(expected==Caches());
   assert(g_video_buffer_read_ptr==input.data()+offset+count*inputStride);
   ++cases;
  }
 }
 std::cout<<"PASS "<<cases<<" full-batch versus tail CPU-cache comparisons; "
          <<"indexed s16 positions/normals/texcoords, RGBA8888, matrix IDs, "
          <<"0..128 vertices, unaligned input, final-record skip masks. "
          <<"No GPU/output/performance claim.\n";
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    spec = importlib.util.spec_from_file_location('vertex_fixture', BASE)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    # Explicitly reviewed current sources; keep the historical unroll probe's
    # original pins unchanged. Its main still rejects any unreviewed source drift.
    fixture.PINS.update({
        'VertexLoader_Position': '8ec0d962e04b565066a5cc9743061fa36e1f9cf6b39cbea4e859d9f1684bcf0d',
        'VertexLoader_Normal': '6e611de10a33f7a0aebad5552a482b88c1d3f232e521fb603c583fb351c5b5d8',
        'VertexLoader_TextCoord': '3fbffffb06f7f42653bb53674c3ec763b1046fbb6b1a5a9fc022d03b0f5c8693',
    })
    saved_args = sys.argv
    fmt_include = fixture.ROOT / 'ref/ModernGekko/vendor/fmt/fmt/include'
    saved_include = os.environ.get('CPLUS_INCLUDE_PATH')
    try:
        sys.argv = [str(BASE), '--output', str(out)]
        os.environ['CPLUS_INCLUDE_PATH'] = str(fmt_include)
        fixture.main()
    finally:
        sys.argv = saved_args
        if saved_include is None:
            os.environ.pop('CPLUS_INCLUDE_PATH', None)
        else:
            os.environ['CPLUS_INCLUDE_PATH'] = saved_include
    source = (fixture.CORE / 'VideoCommon/VertexLoader.cpp').read_text()
    callbacks = out / 'callbacks.cpp'
    text = callbacks.read_text()
    signature = 'void Configure(VertexLoader& l,int config) {'
    assert text.count(signature) == 1
    text = text.replace(signature, fixture.function(source, 'static void PosMtx_ReadDirect_UByte(')
                        + signature)
    text = text.replace(' l.m_PipelineStages.push_back(Pos_ReadIndex',
                        ' l.m_PipelineStages.push_back(PosMtx_ReadDirect_UByte);\n'
                        ' l.m_PipelineStages.push_back(Pos_ReadIndex')
    text = text.replace('stride=28+config*8', 'stride=32+config*8')
    callbacks.write_text(text)
    (out / 'driver.cpp').write_text(fixture.DRIVER.split('int main(')[0] + DRIVER)
    flags = ['clang++', '-std=c++20', '-O2', '-fno-fast-math', '-ffp-contract=off',
             '-fsanitize=address,undefined', '-I'+str(fixture.CORE),
             '-I'+str(fmt_include), '-I'+str(out)]
    subprocess.run(flags + [str(out / (name+'.cpp')) for name in ('loops', 'callbacks', 'driver')]
                   + ['-o', str(out / 'tail-state')], check=True)
    result = subprocess.check_output([str(out / 'tail-state')], text=True, timeout=60)
    (out / 'tail-state.txt').write_text(result)
    print(result, end='')


if __name__ == '__main__':
    main()
