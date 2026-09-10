"""Compile the proposed canonical transform and require tested-source parity."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
generated = root/'generated/modules-fprf-r174/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-27fc425ac63117e7/dolrecomp-output/RMGE01_generated'
original = generated/'chunks/chunk_1102_text1_804520A0.c'
assert hashlib.sha256(original.read_bytes()).hexdigest() == 'f2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61'
candidate = root/'generated/thp-kernels-r198-exits/candidate.c'
assert hashlib.sha256(candidate.read_bytes()).hexdigest() == '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
expected = candidate.read_text().replace('#include "'+str(generated/'RMGE01.h')+'"','#include "../RMGE01.h"')
policy = (root/'patches/experiments/thp-kernel-policy.inc').read_text()
driver = r'''
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <regex>
#include <sstream>
#include <string>
#include <vector>
namespace fs=std::filesystem;
namespace moderngekko {
std::optional<std::string> HashFileSha256(const fs::path&) { return "wrong"; }
}
POLICY
int main(int argc,char** argv) {
 assert(argc==2);
 const std::string dol="2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09";
 assert(GalaxyThpPolicy("RMGE01",dol,"c",1024)=="rmge01-thp-kernels-2-v1");
 assert(GalaxyThpPolicy("RMGK01",dol,"c",1024)=="none");
 assert(GalaxyThpPolicy("RMGE01","wrong","c",1024)=="none");
 assert(GalaxyThpPolicy("RMGE01",dol,"llvm",1024)=="none");
 assert(GalaxyThpPolicy("RMGE01",dol,"c",4096)=="none");
 assert(!ApplyGalaxyThp("must-not-write"));
 std::ifstream input(argv[1]);
 const std::string source((std::istreambuf_iterator<char>(input)),{});
 const auto result=GalaxyThpTransform(source);assert(result);
 assert(!GalaxyThpTransform(*result));
 auto missing=source;
 auto at=missing.find("label_804526EC:\n");assert(at!=std::string::npos);
 missing.erase(at,std::string("label_804526EC:\n").size());
 assert(!GalaxyThpTransform(missing));
 auto outside=source;
 at=outside.find("goto label_80452750;",outside.find("\nlabel_804526E8:"));assert(at!=std::string::npos);
 outside.replace(at,std::string("goto label_80452750;").size(),"goto label_804520A0;");
 assert(!GalaxyThpTransform(outside));
 auto badcase=source;
 at=badcase.find("case 0x804526ECu:");assert(at!=std::string::npos);
 badcase.replace(at,4,"nope");
 assert(!GalaxyThpTransform(badcase));
 std::cout<<*result;
}
'''.replace('POLICY',policy)
with tempfile.TemporaryDirectory(prefix='galaxypad-thp-policy-') as directory:
    temp = Path(directory)
    (temp/'driver.cpp').write_text(driver)
    subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined',
                    str(temp/'driver.cpp'),'-o',str(temp/'driver')],check=True)
    output = subprocess.check_output([str(temp/'driver'),str(original)],text=True)
    assert output==expected, 'Canonical extraction differs from tested candidate'
print('Canonical THP extraction exactly matches tested candidate; identity/hash/reapply/label/branch/entry guards pass')
