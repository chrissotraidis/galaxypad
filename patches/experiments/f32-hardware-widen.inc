    // Exact widening only for normal finite binary32 inputs.
    const u32 exponent = (value >> 23) & 255u;
    if (exponent - 1u < 254u)
        return f64_bits((f64)f32_value(value));
