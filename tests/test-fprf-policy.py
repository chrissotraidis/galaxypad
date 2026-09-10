"""Compile canonical policy in isolation and compare with tested candidate."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
# Historical experiment reference: selection of a newer module must not change it.
generated = (root/'generated/modules-midblock-r144/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-da63c951ce4d7349/dolrecomp-output').resolve()/'RMGE01_generated'
original = generated/'chunks/chunk_1102_text1_804520A0.c'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '2dc3b915db7bd33c84a0481499fefd0ee91a201bc20cb6540248caf06729d539'
candidate = (root/'generated/fprf-r167'/original.name).read_text().replace(
    '#include "'+str(generated/'RMGE01.h')+'"', '#include "../RMGE01.h"')
policy = (root/'patches/experiments/fprf-module-policy.inc').read_text()
port = (root/'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert policy in port, 'Integrated policy must match the tested source'
assert port.index('const std::string fprf_policy = GalaxyFprfPolicy(') < port.index('if (fs::is_regular_file(module))')
assert '"|fprf_policy=" + fprf_policy' in port
assert '"fprf_policy=" << fprf_policy' in port
assert port.index('!ApplyGalaxyFprf(generated)') < port.index('std::string configure =')
driver = r'''
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <regex>
#include <string>
#include <vector>
namespace fs=std::filesystem;
namespace moderngekko {
std::optional<std::string> HashFileSha256(const fs::path&) { return "wrong"; }
}
POLICY
int main(int argc,char** argv) {
 assert(argc==2);
 const std::string hash="2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09";
 assert(GalaxyFprfPolicy("RMGE01",hash,"c",1024)=="rmge01-fprf-119-v1");
 assert(GalaxyFprfPolicy("RMGJ01",hash,"c",1024)=="none");
 assert(GalaxyFprfPolicy("RMGE01","wrong","c",1024)=="none");
 assert(GalaxyFprfPolicy("RMGE01",hash,"llvm",1024)=="none");
 assert(GalaxyFprfPolicy("RMGE01",hash,"c",512)=="none");
 assert(!ApplyGalaxyFprf("does-not-exist")); // Hash refusal before output open.
 std::ifstream input(argv[1]);
 const std::string source((std::istreambuf_iterator<char>(input)),{});
 const auto transformed=GalaxyFprfTransform(source);
 assert(transformed);
 assert(!GalaxyFprfTransform(*transformed)); // No double application.
 std::string changed=source;
 const auto call=changed.find("ppc_ps_add_op(ctx, 8, 9, 6);");
 assert(call!=std::string::npos);
 changed.insert(call,"return;\n    ");
 assert(!GalaxyFprfTransform(changed)); // Unexpected boundary fails closed.
 std::cout<<*transformed;
}
'''.replace('POLICY',policy)
with tempfile.TemporaryDirectory(prefix='galaxypad-fprf-policy-') as directory:
    temp = Path(directory)
    (temp/'driver.cpp').write_text(driver)
    subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined',
                    str(temp/'driver.cpp'),'-o',str(temp/'driver')],check=True)
    result = subprocess.check_output([str(temp/'driver'),str(original)],text=True)
    assert result == candidate, 'Canonical transform differs from tested candidate'
print('Canonical policy matches tested 119-site candidate; identity/backend/chunk/reapply/barrier guards pass')
