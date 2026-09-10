// Content identity, not mtimes or absolute checkout paths. Missing inputs fail
// closed before cache lookup. Generated game code has its own existing key.
std::optional<std::string> ModuleSourceIdentity(const fs::path& dolphin)
{
  try
  {
    std::vector<fs::path> files;
    for (const auto* directory : {"GXRuntime/src/core", "GXRuntime/include", "module-template"})
    {
      const auto base = dolphin / directory;
      if (!fs::is_directory(base))
        return std::nullopt;
      bool found = false;
      for (const auto& entry : fs::recursive_directory_iterator(base))
      {
        if (entry.is_symlink())
          return std::nullopt;
        if (entry.is_regular_file())
        {
          files.push_back(entry.path().lexically_relative(dolphin));
          found = true;
        }
      }
      if (!found)
        return std::nullopt;
    }
    files.emplace_back("Source/Core/Core/PowerPC/StaticRecomp/StaticRecompABI.h");
    std::sort(files.begin(), files.end());
    std::string identity;
    for (const auto& relative : files)
    {
      const auto hash = moderngekko::HashFileSha256(dolphin / relative);
      if (!hash)
        return std::nullopt;
      const auto name = relative.generic_string();
      identity += std::to_string(name.size()) + ":" + name + ":" + *hash + "\n";
    }
    return identity;
  }
  catch (const fs::filesystem_error&)
  {
    return std::nullopt;
  }
}
