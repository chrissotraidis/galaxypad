// Exact generated-header specialization; callbacks and guest timing are untouched.
std::string GalaxyTwoRangePolicy(const std::string& disc, const std::string& dol,
                                const std::string& backend, unsigned chunks,
                                const std::string& lookup)
{
  return disc == "RMGE01" &&
         dol == "2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09" &&
         backend == "c" && chunks == 1024 && lookup == "indexed" ?
         "rmge01-two-range-v1" : "none";
}

std::optional<std::string> GalaxyTwoRangeTransform(const std::string& source)
{
  const std::string begin = "static inline DolRecompFunction dolrecomp_find_original(u32 address) {";
  const std::string end = "static inline int dolrecomp_call_original(";
  const auto first = source.find(begin);
  const auto last = source.find(end);
  if (first == std::string::npos || last == std::string::npos || last <= first ||
      source.find(begin, first + 1) != std::string::npos ||
      source.find(end, last + 1) != std::string::npos ||
      source.find("u32 offset = address - 0x800070A0u;") != std::string::npos)
    return std::nullopt;
  const std::string replacement = R"(static inline DolRecompFunction dolrecomp_find_original(u32 address) {
    if (address & 3u) return NULL;
    u32 offset = address - 0x800070A0u;
    if (offset < (0x8052D280u - 0x800070A0u))
        return dolrecomp_run_chunks[3u + (offset >> 12)];
    offset = address - 0x80004000u;
    if (offset < (0x800064E0u - 0x80004000u))
        return dolrecomp_run_chunks[offset >> 12];
    return NULL;
}

)";
  return source.substr(0, first) + replacement + source.substr(last);
}

bool ApplyGalaxyTwoRange(const fs::path& generated)
{
  const auto header = generated / "RMGE01.h";
  const auto hash = moderngekko::HashFileSha256(header);
  if (!hash || *hash != "2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9")
    return false;
  std::ifstream input(header, std::ios::binary);
  if (!input) return false;
  const std::string source((std::istreambuf_iterator<char>(input)), {});
  const auto transformed = GalaxyTwoRangeTransform(source);
  if (!transformed) return false;
  input.close();
  std::ofstream output(header, std::ios::binary | std::ios::trunc);
  if (!output) return false;
  output << *transformed;
  output.close();
  return bool(output);
}
