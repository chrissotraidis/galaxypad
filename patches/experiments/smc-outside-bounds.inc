  // Preserve fallback-JIT invalidation and address resolution above. A range
  // outside the sorted code envelope cannot change any chunk verification.
  const u32 count = m_module->num_chunk_ranges;
  if (count == 0 || address >= m_module->chunk_ranges[count - 1].end ||
      last < m_module->chunk_ranges[0].start)
    return;

