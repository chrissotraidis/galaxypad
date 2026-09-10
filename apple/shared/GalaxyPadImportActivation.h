// SPDX-License-Identifier: GPL-3.0-or-later
// SunPad's sibling staging/activation boundary, strengthened to a single atomic
// directory exchange. Old game data stays in staging until explicit cleanup.
#pragma once
#include <filesystem>
#include <string>
#include <system_error>
#include <sys/stdio.h>
#include <cerrno>

namespace galaxypad {
inline bool validImportStageName(const std::string& name) {
  const std::string prefix="GameData.import-";
  if (!name.starts_with(prefix) || name.size()!=prefix.size()+36) return false;
  for (size_t i=0;i<36;++i) {
    char c=name[prefix.size()+i];
    if (i==8||i==13||i==18||i==23) { if (c!='-') return false; }
    else if (!((c>='0'&&c<='9')||(c>='a'&&c<='f')||(c>='A'&&c<='F'))) return false;
  }
  return true;
}
struct ImportActivationResult {
  std::error_code error;
  bool previousDataRetained=false;
};
// Detach only the installed GameData tree before asynchronous deletion. The
// returned stage is owned by the caller; no save/NAND or recovery-stage scan.
inline std::error_code detachInstalledData(const std::filesystem::path& root,
    const std::string& removalName, bool runtimeStopped) {
  namespace fs=std::filesystem;
  const std::string prefix="GameData.removal-";
  if (!runtimeStopped || !root.is_absolute() || !removalName.starts_with(prefix) ||
      !validImportStageName("GameData.import-"+removalName.substr(prefix.size())))
    return std::make_error_code(std::errc::invalid_argument);
  std::error_code error;
  if (!fs::is_directory(fs::symlink_status(root,error)) || error)
    return error?error:std::make_error_code(std::errc::not_a_directory);
  auto active=root/"GameData";
  if (!fs::is_directory(fs::symlink_status(active,error)) || error)
    return error?error:std::make_error_code(std::errc::not_a_directory);
  if (renamex_np(active.c_str(),(root/removalName).c_str(),RENAME_EXCL)!=0)
    return std::error_code(errno,std::generic_category());
  return {};
}
// Call only for a fully verified stage, with exclusive import ownership and
// a confirmed stopped runtime. This operation never touches save/NAND paths.
inline ImportActivationResult activateImport(const std::filesystem::path& root,
    const std::string& stageName, bool runtimeStopped) {
  namespace fs=std::filesystem;
  if (!runtimeStopped || !validImportStageName(stageName) || !root.is_absolute())
    return {std::make_error_code(std::errc::invalid_argument),false};
  std::error_code error;
  auto rootStatus=fs::symlink_status(root,error);
  if (error || !fs::is_directory(rootStatus))
    return {error?error:std::make_error_code(std::errc::not_a_directory),false};
  auto stage=root/stageName, active=root/"GameData";
  auto stageStatus=fs::symlink_status(stage,error);
  if (error || !fs::is_directory(stageStatus))
    return {error?error:std::make_error_code(std::errc::not_a_directory),false};
  auto activeStatus=fs::symlink_status(active,error);
  if (error==std::errc::no_such_file_or_directory) error.clear();
  if (error) return {error,false};
  bool replacing=fs::exists(activeStatus);
  if (replacing && !fs::is_directory(activeStatus))
    return {std::make_error_code(std::errc::not_a_directory),false};
  // EXCL prevents a racing first activation from overwriting an existing tree.
  // SWAP has no intermediate missing-active state and preserves the old tree.
  if (renamex_np(stage.c_str(),active.c_str(),replacing?RENAME_SWAP:RENAME_EXCL)!=0)
    return {std::error_code(errno,std::generic_category()),false};
  return {{},replacing};
}
}
