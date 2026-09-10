"""Compile the patched runner's actual option parser with its real RuntimeConfig."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = root/'ref/ModernGekko/tools/moderngekko_run.cpp'
patch = root/'patches/experiments/runner-background-input.patch'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '967accdf84004447f7bafb53821ac0f2d86ddfa7e6971df15668b7dcef9735a7'
with tempfile.TemporaryDirectory(prefix='galaxypad-input-parser-') as tmp:
    base = Path(tmp)
    (base/'tools').mkdir()
    target = base/'tools/moderngekko_run.cpp'
    target.write_bytes(source.read_bytes())
    subprocess.run(['git','apply',str(patch)], cwd=base, check=True)
    modified = target.read_text()
    parser = modified.split('  moderngekko::RuntimeConfig config;',1)[1].split('  if (config.game_root.empty())',1)[0]
    code = r'''
#include <moderngekko/runtime.hpp>
#include <charconv>
#include <cstdlib>
#include <iostream>
namespace moderngekko::frontend { enum class NetplayRole { Host, Join }; }
std::filesystem::path DefaultUserDirectory() { return {}; }
std::filesystem::path ExecutableDirectory(const char*) { return {}; }
void Usage() { std::cout << "help\n"; }
int main(int argc, char** argv) {
  moderngekko::RuntimeConfig config;
''' + parser + r'''
  std::cout << "background=" << config.input.background_input
            << " interpreter=" << config.allow_interpreter << "\n";
}
'''
    cpp = base/'test.cpp'
    cpp.write_text(code)
    exe = base/'test'
    subprocess.run(['c++','-std=c++20','-fsanitize=address,undefined',
                    '-I'+str(root/'ref/ModernGekko/include'),str(cpp),'-o',str(exe)],check=True)
    cases = [([],0,'background=0 interpreter=0'),
             (['--background-input'],0,'background=1 interpreter=0'),
             (['--background-input','--background-input'],0,'background=1 interpreter=0'),
             (['--game','--background-input'],0,'background=0 interpreter=0'),
             (['--background-input','--allow-interpreter'],0,'background=1 interpreter=1'),
             (['--background-input=false'],2,None),
             (['--background-input','--game'],2,None),
             (['--help'],0,'help')]
    for args, expected_code, expected_text in cases:
        result = subprocess.run([str(exe),*args],capture_output=True,text=True)
        assert result.returncode == expected_code, result.stderr
        if expected_text:
            assert expected_text in result.stdout, result.stdout
    subprocess.run(['git','apply','--reverse',str(patch)],cwd=base,check=True)
    assert target.read_bytes() == source.read_bytes()
print('Actual runner parser: default-off, exact opt-in, repeats, value boundary, malformed arguments and reversal pass')
