  // Run-scoped metadata: LoadModule/InitLookupTable precede this invocation.
  // Verification bytes remain live: invalidation and ClearCache must be visible.
  const bool general_lookup = m_has_rel_modules || !m_forced_fallback_ranges.empty();
  const int* const lookup_data = m_chunk_lookup_table.data();
  const int lookup_count = static_cast<int>(m_chunk_lookup_table.size());
  const u32 lookup_ram_size = m_lookup_ram_size;
  const u32 lookup_exram_size = m_lookup_exram_size;
  const u8* const chunk_states = m_chunk_state.data();
  const auto fast_dispatchable_at = [&, this](u32 address) {
    if (general_lookup)
      return FastDispatchableAt(address);
    if (!m_module_active || lookup_count == 0)
      return false;

    int lookup_index = -1;
    if (address >= 0x80000000u && address < 0x80000000u + lookup_ram_size)
      lookup_index = static_cast<int>((address - 0x80000000u) >> 2);
    else if (address >= 0x90000000u && address < 0x90000000u + lookup_exram_size)
      lookup_index = static_cast<int>((lookup_ram_size >> 2) + ((address - 0x90000000u) >> 2));
    if (lookup_index < 0 || lookup_index >= lookup_count)
      return false;
    const int chunk = lookup_data[lookup_index];
    return chunk >= 0 && chunk_states[chunk] == CHUNK_VERIFIED;
  };
