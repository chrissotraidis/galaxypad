// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadImportActivation.h"
#include <cassert>
#include <fstream>
#include <cstdlib>
#include <unistd.h>
#include <cstdio>
namespace fs=std::filesystem;
static std::string read(const fs::path& path) {
  std::ifstream file(path); std::string value; file>>value; return value;
}
int main() {
  char pattern[]="/tmp/galaxypad-import-test.XXXXXX";
  char* created=mkdtemp(pattern); assert(created);
  fs::path root=created;
  const std::string stage="GameData.import-00000000-0000-0000-0000-000000000001";
  assert(galaxypad::validImportStageName(stage));
  for (const auto& bad:{"GameData", "../GameData", "GameData.import-../save", "GameData.import-not-a-uuid"})
    assert(!galaxypad::validImportStageName(bad));
  fs::create_directory(root/stage);
  std::ofstream(root/stage/"marker")<<"first";
  fs::create_directory(root/"Wii");
  std::ofstream(root/"Wii"/"save")<<"preserve";
  auto blocked=galaxypad::activateImport(root,stage,false);
  assert(blocked.error && fs::exists(root/stage/"marker") && !fs::exists(root/"GameData"));
  auto first=galaxypad::activateImport(root,stage,true);
  assert(!first.error && !first.previousDataRetained && read(root/"GameData"/"marker")=="first");
  fs::create_directory(root/stage);
  std::ofstream(root/stage/"marker")<<"second";
  auto second=galaxypad::activateImport(root,stage,true);
  assert(!second.error && second.previousDataRetained);
  assert(read(root/"GameData"/"marker")=="second" && read(root/stage/"marker")=="first");
  auto rollback=galaxypad::activateImport(root,stage,true); // same atomic exchange restores prior data
  assert(!rollback.error && read(root/"GameData"/"marker")=="first");
  assert(read(root/"Wii"/"save")=="preserve");
  const std::string missing="GameData.import-00000000-0000-0000-0000-000000000002";
  assert(galaxypad::activateImport(root,missing,true).error);
  fs::create_directory_symlink(root/"Wii",root/missing);
  assert(galaxypad::activateImport(root,missing,true).error);
  assert(read(root/"GameData"/"marker")=="first" && read(root/"Wii"/"save")=="preserve");
  const std::string removal="GameData.removal-00000000-0000-0000-0000-000000000003";
  assert(galaxypad::detachInstalledData(root,removal,false));
  assert(galaxypad::detachInstalledData(root,"../Wii",true));
  fs::create_directory(root/removal);
  assert(galaxypad::detachInstalledData(root,removal,true)); // cannot overwrite
  assert(read(root/"GameData"/"marker")=="first");
  fs::remove(root/removal);
  assert(!galaxypad::detachInstalledData(root,removal,true));
  assert(!fs::exists(root/"GameData") && read(root/removal/"marker")=="first");
  fs::remove_all(root/removal); // Simulate worker deletion of owned detached tree.
  assert(read(root/"Wii"/"save")=="preserve" && read(root/stage/"marker")=="second");
  fs::create_directory_symlink(root/"Wii",root/"GameData");
  assert(galaxypad::detachInstalledData(root,removal,true));
  assert(read(root/"Wii"/"save")=="preserve");
  fs::remove_all(root); // Only this test's mkdtemp directory and synthetic files.
  puts("Atomic import activation, rollback, runtime gate and save isolation pass");
}
