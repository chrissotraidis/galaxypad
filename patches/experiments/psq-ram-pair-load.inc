        // Experimental only. A fully mapped pair has no external callbacks.
        // Preserve lane order even if guest RAM aliases the destination FPR.
        if (!w && cpu->ram_size >= 8u && cpu->ram_size <= 0x10000000u &&
            (!cpu->exram || (cpu->exram_size >= 8u && cpu->exram_size <= 0x10000000u))) {
            u8* pair = get_ram_ptr(cpu, ea, 8u, NULL);
            if (pair) {
                cpu->fpr[frD] = f64_value(convert_to_double(read_be32(pair)));
                cpu->ps1[frD] = f64_value(convert_to_double(read_be32(pair + 4u)));
                return true;
            }
        }
