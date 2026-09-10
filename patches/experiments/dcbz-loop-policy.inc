// Private opt-in only; policy identity is part of the module cache key.
std::string GalaxyDcbzPolicy(const std::string& disc, const std::string& dol,
                            const std::string& backend, unsigned chunks)
{
  const char* enabled = std::getenv("GALAXYPAD_DCBZ_LOOP");
  return enabled && std::string(enabled) == "1" && disc == "RMGE01" &&
      dol == "2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09" &&
      backend == "c" && chunks == 1024 ? "rmge01-dcbz-loop-8-v1" : "none";
}

const char* GalaxyDcbzHelper = R"GXR(/* Preserve the generated loop for profile matching; specialize its stores. */
static inline u8* galaxypad_dcbz_prepare(CPUState* cpu, u32 ea) {
    if (!g_mem_write_journal && cpu->ram &&
        cpu->ram_size >= 32u && cpu->ram_size <= 0x10000000u &&
        (!cpu->exram || (cpu->exram_size >= 32u && cpu->exram_size <= 0x10000000u))) {
        u8* line = get_ram_ptr(cpu, ea, 32u, NULL);
        if (line) {
            const uintptr_t begin = (uintptr_t)line;
            const uintptr_t state = (uintptr_t)cpu;
            const uintptr_t journal = (uintptr_t)&g_mem_write_journal;
            const bool state_disjoint = begin >= state ?
                begin - state >= sizeof(*cpu) : state - begin >= 32u;
            const bool journal_disjoint = begin >= journal ?
                begin - journal >= sizeof(g_mem_write_journal) : journal - begin >= 32u;
            if (state_disjoint && journal_disjoint) {
                clear_matching_reservation(cpu, ea);
                return line;
            }
        }
    }
    return NULL;
}
static inline void galaxypad_dcbz_store(CPUState* cpu, u32 ea, u8* line, u32 i) {
    if (line) write_be32(line + i, 0);
    else mem_write32(cpu, ea + i, 0);
}
static inline void galaxypad_dcbz_ram_line(CPUState* cpu, u32 address) {
    const u32 ea = address & ~31u;
    u8* line = galaxypad_dcbz_prepare(cpu, ea);
    for (u32 i = 0; i < 32; i += 4)
        galaxypad_dcbz_store(cpu, ea, line, i);
}
)GXR";

std::optional<std::string> GalaxyDcbzTransform(std::string source)
{
  const std::string signature = "void func_804530A0(CPUState* ctx) {";
  const auto function = source.find(signature);
  if (function == std::string::npos ||
      source.find(signature, function + 1) != std::string::npos ||
      source.find("galaxypad_dcbz_") != std::string::npos)
    return std::nullopt;
  const std::string before = "for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);";
  const std::string after = "u8* line = galaxypad_dcbz_prepare(ctx, ea);\n"
      "        for (u32 i = 0; i < 32; i += 4) galaxypad_dcbz_store(ctx, ea, line, i);";
  unsigned count = 0;
  for (std::size_t at = 0; (at = source.find(before, at)) != std::string::npos; at += after.size())
  {
    source.replace(at, before.size(), after);
    ++count;
  }
  if (count != 8) return std::nullopt;
  source.insert(source.find(signature), std::string("#include <string.h>\n") + GalaxyDcbzHelper + "\n");
  return source;
}

bool ApplyGalaxyDcbz(const fs::path& generated)
{
  const auto chunk = generated / "chunks/chunk_1103_text1_804530A0.c";
  const auto hash = moderngekko::HashFileSha256(chunk);
  if (!hash || *hash != "e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc")
  {
    std::cerr << "Unexpected RMGE01 decoder source identity; refusing build\n";
    return false;
  }
  std::ifstream input(chunk, std::ios::binary);
  const std::string source((std::istreambuf_iterator<char>(input)), {});
  const auto transformed = GalaxyDcbzTransform(source);
  if (!transformed) return false;
  std::ofstream output(chunk, std::ios::binary | std::ios::trunc);
  output << *transformed;
  output.close();
  return static_cast<bool>(output);
}
