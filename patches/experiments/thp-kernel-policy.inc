// Exact RMGE01 transform extraction, applied after the accepted FPRF policy.
std::string GalaxyThpPolicy(const std::string& disc, const std::string& dol,
                           const std::string& backend, unsigned chunks)
{
  return disc == "RMGE01" &&
         dol == "2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09" &&
         backend == "c" && chunks == 1024 ? "rmge01-thp-kernels-2-v1" : "none";
}

void GalaxyThpReplace(std::string& text, const std::string& from, const std::string& to)
{
  for (std::size_t at = 0; (at = text.find(from, at)) != std::string::npos; at += to.size())
    text.replace(at, from.size(), to);
}

std::optional<std::string> GalaxyThpTransform(const std::string& source)
{
  const std::string signature = "void func_804520A0(CPUState* ctx) {";
  const auto function = source.find(signature);
  if (function == std::string::npos || source.find(signature, function + 1) != std::string::npos ||
      source.find("thp_kernel_") != std::string::npos)
    return std::nullopt;
  const auto prefix = source.substr(0, function);
  auto outer = source.substr(function + signature.size());
  const auto switch_end = outer.find("    default: return;");
  if (switch_end == std::string::npos) return std::nullopt;
  const auto entry = outer.substr(0, switch_end);
  const unsigned starts[] = {0x804526e8, 0x80452b74, 0x80453008};
  const auto hex = [](unsigned pc) {
    std::ostringstream stream;
    stream << std::uppercase << std::hex << pc;
    return stream.str();
  };
  const std::regex labels(R"(^label_([0-9A-F]{8}):)", std::regex::multiline);
  const std::regex cases(R"(^    case 0x([0-9A-F]{8})u: (?:ctx->downcount -= [0-9]+; )?goto label_([0-9A-F]{8});$)", std::regex::multiline);
  const std::regex charge(R"(ctx->downcount -= [0-9]+; )");
  const std::regex jumps(R"(goto (\w+);)");
  std::string kernels;
  std::vector<std::pair<std::string, std::string>> replacements;
  for (unsigned index = 0; index < 2; ++index)
  {
    const auto begin = outer.find("\nlabel_" + hex(starts[index]) + ":");
    const auto end = outer.find("\nlabel_" + hex(starts[index + 1]) + ":");
    if (begin == std::string::npos || end == std::string::npos || end <= begin)
      return std::nullopt;
    const auto body = outer.substr(begin, end - begin);
    unsigned expected = starts[index];
    std::vector<std::string> names;
    for (auto i = std::sregex_iterator(body.begin(), body.end(), labels);
         i != std::sregex_iterator(); ++i, expected += 4)
    {
      if ((*i)[1].str() != hex(expected)) return std::nullopt;
      names.push_back((*i)[1].str());
    }
    if (expected != starts[index + 1]) return std::nullopt;
    bool returns = false;
    for (auto i = std::sregex_iterator(body.begin(), body.end(), jumps);
         i != std::sregex_iterator(); ++i)
    {
      const auto target = (*i)[1].str();
      if (target == "return_dispatch_804520A0") { returns = true; continue; }
      bool found = false;
      for (const auto& name : names) found |= target == "label_" + name;
      if (!found) return std::nullopt;
    }
    if (!returns) return std::nullopt;
    std::string kernel_cases;
    expected = starts[index];
    for (auto i = std::sregex_iterator(entry.begin(), entry.end(), cases);
         i != std::sregex_iterator(); ++i)
    {
      const auto pc = std::stoul((*i)[1].str(), nullptr, 16);
      if (pc < starts[index] || pc >= starts[index + 1]) continue;
      if (pc != expected || (*i)[1] != (*i)[2]) return std::nullopt;
      kernel_cases += std::regex_replace(i->str(), charge, "") + "\n";
      expected += 4;
    }
    if (expected != starts[index + 1]) return std::nullopt;
    auto kernel_body = body;
    GalaxyThpReplace(kernel_body, "return;", "return false;");
    const auto id = std::to_string(index);
    kernels += "static __attribute__((noinline, flatten)) bool thp_kernel_" + id +
               "(CPUState* ctx) {\n    switch (ctx->pc) {\n" + kernel_cases +
               "    default: return false;\n    }\n" + kernel_body +
               "\nreturn_dispatch_804520A0: return true;\n}\n\n";
    std::string trampolines;
    for (const auto& name : names)
      trampolines += "\nlabel_" + name + ":\n    ctx->pc = 0x" + name +
                     "u;\n    goto invoke_thp_" + id + ";\n";
    trampolines += "\ninvoke_thp_" + id + ":\n    if (!thp_kernel_" + id +
                   "(ctx)) return;\n    goto return_dispatch_804520A0;\n";
    outer.replace(begin, body.size(), trampolines);
    replacements.emplace_back(trampolines, body);
  }
  auto restored = outer;
  for (const auto& change : replacements)
  {
    const auto at = restored.find(change.first);
    if (at == std::string::npos) return std::nullopt;
    restored.replace(at, change.first.size(), change.second);
  }
  if (prefix + signature + restored != source || outer.substr(0, switch_end) != entry)
    return std::nullopt;
  return prefix + kernels + signature + outer;
}

bool ApplyGalaxyThp(const fs::path& generated)
{
  const auto chunk = generated / "chunks/chunk_1102_text1_804520A0.c";
  const auto hash = moderngekko::HashFileSha256(chunk);
  if (!hash || *hash != "f2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61")
  {
    std::cerr << "Unexpected RMGE01 THP source identity; refusing build\n";
    return false;
  }
  std::ifstream input(chunk, std::ios::binary);
  const std::string source((std::istreambuf_iterator<char>(input)), {});
  const auto transformed = GalaxyThpTransform(source);
  if (!transformed) return false;
  std::ofstream output(chunk, std::ios::binary | std::ios::trunc);
  output << *transformed;
  output.close();
  return static_cast<bool>(output);
}
