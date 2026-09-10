// Unselected experiment. Caller must exclude host/lockstep write journaling,
// propagate guest MSR first, and use the returned pointer immediately only.
u8* MMU::TryGetLockedCachePair(u32 address)
{
  if (m_power_pc.GetMemChecks().HasAny() || m_ppc_state.m_enable_dcache ||
      StaticRecompLockstep::g_lc_write_journal || StaticRecompLockstep::g_hw_write_sink)
    return nullptr;
  // Reject page crossing and integer wrap before translating either byte.
  if ((address & (BAT_PAGE_SIZE - 1)) == BAT_PAGE_SIZE - 1)
    return nullptr;
  if (m_ppc_state.msr.DR)
  {
    const u32 bat = m_dbat_table[address >> BAT_INDEX_SHIFT];
    if ((bat & (BAT_MAPPED_BIT | BAT_PHYSICAL_BIT)) != (BAT_MAPPED_BIT | BAT_PHYSICAL_BIT))
      return nullptr;
    address = (bat & BAT_RESULT_MASK) | (address & (BAT_PAGE_SIZE - 1));
  }
  constexpr u32 base = 0xE0000000u;
  const u32 size = m_memory.GetL1CacheSize();
  if (!m_memory.GetL1Cache() || size < 2 || address < base || address - base > size - 2)
    return nullptr;
  return m_memory.GetL1Cache() + (address - base);
}
