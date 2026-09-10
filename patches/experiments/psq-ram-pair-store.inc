        // Prototype only: no callback can intervene on this direct-RAM path.
        // Keep conversion, reservation invalidation, and stores lane-ordered.
        if (!w && !g_mem_write_journal && cpu->ram_size >= 8u &&
            (!cpu->exram || cpu->exram_size >= 8u)) {
            u8* pair = get_ram_ptr(cpu, ea, 8u, NULL);
            if (pair && ((uintptr_t)pair + 8u <= (uintptr_t)cpu ||
                         (uintptr_t)pair >= (uintptr_t)cpu + sizeof(*cpu))) {
                u32 value = convert_to_single_ftz(f64_bits(cpu->fpr[frS]));
                clear_matching_reservation(cpu, ea);
                write_be32(pair, value);
                value = convert_to_single_ftz(f64_bits(cpu->ps1[frS]));
                clear_matching_reservation(cpu, ea + 4u);
                write_be32(pair + 4u, value);
                return true;
            }
        }
