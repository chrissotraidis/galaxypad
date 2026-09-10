    // Integer-only normal-result path; special values use original logic.
    if (__builtin_expect(exponent != 0 && exponent != 0x7F800000u, 1))
        return 0x04u << sign;
