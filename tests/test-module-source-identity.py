"""Compile the cache-input collector; content hash provider is a test double."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
helper = (root / 'patches/experiments/module-source-identity.inc').read_text()
port = (root / 'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert helper in port, 'Collector must be integrated exactly as tested'
assert port.index('const auto module_sources = ModuleSourceIdentity(') < port.index('if (fs::is_regular_file(module))')
assert '"|module_sources=" + source_fingerprint.str()' in port
assert '"module_sources_fnv1a=" << source_fingerprint.str()' in port
fnv = 'std::uint64_t Fnv1a(' + port.split('std::uint64_t Fnv1a(', 1)[1].split('\n// Content identity', 1)[0]
prefix = r'''
#include <filesystem>
#include <fstream>
#include <optional>
#include <string>
#include <vector>
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <string_view>
namespace fs = std::filesystem;
namespace moderngekko {
std::optional<std::string> HashFileSha256(const fs::path& p) {
  std::ifstream f(p); if (!f) return std::nullopt;
  return std::string(std::istreambuf_iterator<char>(f), {});
}
}
'''
test = r'''
void write(const fs::path& p, const std::string& content) {
  fs::create_directories(p.parent_path()); std::ofstream(p) << content;
}
int main(int argc, char** argv) {
  fs::path a=fs::path(argv[1])/"a", b=fs::path(argv[1])/"b";
  const std::vector<std::string> names={"GXRuntime/src/core/cpu.c",
    "GXRuntime/include/core/types.h", "module-template/CMakeLists.txt",
    "Source/Core/Core/PowerPC/StaticRecomp/StaticRecompABI.h"};
  assert(!ModuleSourceIdentity(a));
  for (auto& n:names) write(a/n,"original");
  for (auto i=names.rbegin();i!=names.rend();++i) write(b/ *i,"original");
  auto original=ModuleSourceIdentity(a); assert(original);
  auto key=Fnv1a("unchanged-options|module_sources="+std::to_string(Fnv1a(*original)));
  assert(ModuleSourceIdentity(b)==original); // creation order / checkout path
  for (auto& n:names) {
    write(a/n,"modified"); assert(ModuleSourceIdentity(a)!=original);
    assert(Fnv1a("unchanged-options|module_sources="+std::to_string(Fnv1a(*ModuleSourceIdentity(a))))!=key);
    write(a/n,"original"); assert(ModuleSourceIdentity(a)==original);
  }
  write(a/"GXRuntime/include/new.h","new");
  assert(ModuleSourceIdentity(a)!=original);
  fs::remove(a/"GXRuntime/include/new.h");
  fs::rename(a/names[0],a/"GXRuntime/src/core/renamed.c");
  assert(ModuleSourceIdentity(a)!=original);
  fs::rename(a/"GXRuntime/src/core/renamed.c",a/names[0]);
  fs::create_symlink(a/names[0],a/"GXRuntime/include/link.h");
  assert(!ModuleSourceIdentity(a));
  fs::remove(a/"GXRuntime/include/link.h");
  fs::remove(a/names[3]); assert(!ModuleSourceIdentity(a));
}
'''
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    source = tmp / 'test.cpp'
    source.write_text(prefix + fnv + helper + test)
    subprocess.run(['clang++', '-std=c++17', '-fsanitize=address,undefined',
                    str(source), '-o', str(tmp / 'test')], check=True)
    subprocess.run([str(tmp / 'test'), str(tmp / 'data')], check=True)
print('Module source identity content/path/order/missing/symlink checks passed')
