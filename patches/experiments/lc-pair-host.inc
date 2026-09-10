  // Size zero negotiates an immediate two-byte write pointer. Old hosts
  // reject it. Keep failure side-effect-free for the sequential fallback.
  if (size == 0)
  {
    static const bool enabled = [] {
      const char* setting = std::getenv("GALAXYPAD_LC_PAIR_FAST");
      const char* tracing = std::getenv("GALAXYPAD_PIXEL_STORE_TRACE");
      return setting && setting[0] == '1' && setting[1] == '\0' &&
             !(tracing && tracing[0] == '1' && tracing[1] == '\0');
    }();
    if (!enabled || (ea >> 28) != 0xE ||
        core->m_lockstep_verifier->m_ls_journaling ||
        cpu->msr != core->m_system.GetPPCState().msr.Hex)
      return nullptr;
    // Do not bypass relocation lookup. A relocated pair uses the old path.
    if (core->TranslateRelAddress(ea) != ea || core->TranslateRelAddress(ea + 1) != ea + 1)
      return nullptr;
    return core->m_system.GetMMU().TryGetLockedCachePair(ea);
  }
