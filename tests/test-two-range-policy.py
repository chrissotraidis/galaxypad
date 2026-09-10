"""Compiled canonical policy parity with the exact runtime-tested header."""
import hashlib
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
original = root/'generated/modules-thp-r205/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-daa33a86eff05b70/dolrecomp-output/RMGE01_generated/RMGE01.h'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9'
expected = root/'generated/two-range-r358/candidate/RMGE01.h'
policy = (root/'patches/experiments/two-range-policy.inc').read_text()
driver = r'''
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <string>
namespace fs=std::filesystem;
std::string accepted;
std::string read(const fs::path& path) {
  std::ifstream stream(path,std::ios::binary);
  return std::string((std::istreambuf_iterator<char>(stream)),{});
}
namespace moderngekko {
// Deterministic hash-provider seam: only the verified input is accepted.
std::optional<std::string> HashFileSha256(const fs::path& path) {
  if(!fs::is_regular_file(path)) return std::nullopt;
  return read(path)==accepted ? "2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9" : "wrong";
}
}
POLICY
int main(int argc,char**argv) {
  assert(argc==3); accepted=read(argv[1]);
  const std::string dol="2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09";
  assert(GalaxyTwoRangePolicy("RMGE01",dol,"c",1024,"indexed")=="rmge01-two-range-v1");
  assert(GalaxyTwoRangePolicy("RMGJ01",dol,"c",1024,"indexed")=="none");
  assert(GalaxyTwoRangePolicy("RMGE01","wrong","c",1024,"indexed")=="none");
  assert(GalaxyTwoRangePolicy("RMGE01",dol,"llvm",1024,"indexed")=="none");
  assert(GalaxyTwoRangePolicy("RMGE01",dol,"c",512,"indexed")=="none");
  assert(GalaxyTwoRangePolicy("RMGE01",dol,"c",1024,"switch")=="none");
  auto transformed=GalaxyTwoRangeTransform(accepted); assert(transformed);
  assert(!GalaxyTwoRangeTransform(*transformed));
  assert(!GalaxyTwoRangeTransform("missing"));
  assert(!GalaxyTwoRangeTransform(accepted+accepted));
  const fs::path directory=argv[2];
  assert(!ApplyGalaxyTwoRange(directory));
  const auto header=directory/"RMGE01.h";
  {std::ofstream out(header);out<<accepted<<"unexpected";}
  assert(!ApplyGalaxyTwoRange(directory));
  assert(read(header)==accepted+"unexpected");
  {std::ofstream out(header);out<<accepted;}
  assert(ApplyGalaxyTwoRange(directory));
  assert(read(header)==*transformed);
  assert(!ApplyGalaxyTwoRange(directory));
  assert(read(header)==*transformed);
  std::cout<<*transformed;
}
'''.replace('POLICY', policy)
with tempfile.TemporaryDirectory(prefix='galaxypad-two-range-policy-') as directory:
    temp = Path(directory)
    (temp/'driver.cpp').write_text(driver)
    subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined',
                    str(temp/'driver.cpp'),'-o',str(temp/'driver')],check=True)
    output = subprocess.check_output([str(temp/'driver'),str(original),str(temp)],text=True)
    assert output == expected.read_text(), 'Canonical lookup differs from runtime-tested header'
print('Compiled two-range policy matches runtime-tested header; eligibility, hash refusal and reapply guards pass')
