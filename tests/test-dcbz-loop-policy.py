"""Compile the proposed build policy and compare its output to tested source."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
module=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
original=module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1103_text1_804530A0.c'
text=original.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
helper=(root/'patches/experiments/dcbz-ram-loop.inc').read_text()
assert hashlib.sha256(helper.encode()).hexdigest()=='ed743fdeb1b32af89dfd1fbfefa671a63b2a36ed7c2c59b684f105275783a421'
policy=(root/'patches/experiments/dcbz-loop-policy.inc').read_text()
assert policy.split('R"GXR(',1)[1].split(')GXR";',1)[0]==helper
anchor='for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);'
assert text.count(anchor)==8
expected=text.replace(anchor,'u8* line = galaxypad_dcbz_prepare(ctx, ea);\n        for (u32 i = 0; i < 32; i += 4) galaxypad_dcbz_store(ctx, ea, line, i);')
expected=expected.replace('void func_804530A0(CPUState* ctx) {','#include <string.h>\n'+helper+'\nvoid func_804530A0(CPUState* ctx) {')
driver=r'''
#include <cassert>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <string>
namespace fs=std::filesystem;
namespace moderngekko {
std::optional<std::string> HashFileSha256(const fs::path&) {return "wrong";}
}
POLICY
int main(int argc,char** argv) {
 assert(argc==2);
 const std::string dol="2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09";
 unsetenv("GALAXYPAD_DCBZ_LOOP");
 assert(GalaxyDcbzPolicy("RMGE01",dol,"c",1024)=="none");
 for(const char* setting:{"0","true","01","","2"}) {
  setenv("GALAXYPAD_DCBZ_LOOP",setting,1);
  assert(GalaxyDcbzPolicy("RMGE01",dol,"c",1024)=="none");
 }
 setenv("GALAXYPAD_DCBZ_LOOP","1",1);
 assert(GalaxyDcbzPolicy("RMGE01",dol,"c",1024)=="rmge01-dcbz-loop-8-v1");
 assert(GalaxyDcbzPolicy("RMGK01",dol,"c",1024)=="none");
 assert(GalaxyDcbzPolicy("RMGE01","wrong","c",1024)=="none");
 assert(GalaxyDcbzPolicy("RMGE01",dol,"llvm",1024)=="none");
 assert(GalaxyDcbzPolicy("RMGE01",dol,"c",4096)=="none");
 assert(!ApplyGalaxyDcbz("must-not-write"));
 std::ifstream input(argv[1]);std::string source((std::istreambuf_iterator<char>(input)),{});
 const auto result=GalaxyDcbzTransform(source);assert(result);
 assert(!GalaxyDcbzTransform(*result));
 const std::string loop="for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);";
 auto missing=source;missing.erase(missing.find(loop),loop.size());
 assert(!GalaxyDcbzTransform(missing));assert(!GalaxyDcbzTransform(source+loop));
 assert(!GalaxyDcbzTransform(source+"void func_804530A0(CPUState* ctx) {"));
 assert(!GalaxyDcbzTransform("wrong"));
 std::cout<<*result;
}
'''.replace('POLICY',policy)
with tempfile.TemporaryDirectory(prefix='galaxypad-dcbz-policy-') as directory:
    temp=Path(directory);(temp/'test.cpp').write_text(driver)
    subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined',str(temp/'test.cpp'),'-o',str(temp/'test')],check=True)
    result=subprocess.run([str(temp/'test'),str(original)],check=True,capture_output=True,text=True)
    assert result.stdout==expected
print('Dcbz policy opt-in/identity/rejection guards and byte-exact tested-source parity passed')
