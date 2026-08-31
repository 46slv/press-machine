"""Reference scalar transfer for SatComp high-saturation compression.

This module deliberately does not define how saturation is measured from RGB.
The color-space/measurement layer must provide a non-negative scalar S and then
reconstruct the color while preserving the selected lightness/hue invariants.
"""

from __future__ import annotations

import math


def compress_saturation(
    saturation: float,
    *,
    threshold: float,
    ratio: float,
    knee: float = 0.0,
) -> float:
    """Compress saturation above ``threshold`` with an optional soft knee.

    Contract:
    - saturation >= 0
    - threshold >= 0
    - ratio >= 1 (1 means exact identity)
    - knee >= 0
    - no ceiling/clamp is applied

    With knee > 0 this is the standard quadratic soft-knee compressor curve,
    adapted to a saturation scalar. It is C1-continuous at both knee edges.
    """
    values = (saturation, threshold, ratio, knee)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("all inputs must be finite")
    if saturation < 0.0:
        raise ValueError("saturation must be >= 0")
    if threshold < 0.0:
        raise ValueError("threshold must be >= 0")
    if ratio < 1.0:
        raise ValueError("ratio must be >= 1")
    if knee < 0.0:
        raise ValueError("knee must be >= 0")

    # Exact bypass is important for a predictable Identity state.
    if ratio == 1.0:
        return saturation

    if knee == 0.0:
        if saturation <= threshold:
            return saturation
        return threshold + (saturation - threshold) / ratio

    half_knee = 0.5 * knee
    lower = threshold - half_knee
    upper = threshold + half_knee

    if saturation <= lower:
        return saturation
    if saturation >= upper:
        return threshold + (saturation - threshold) / ratio

    # Quadratic interpolation whose derivative moves continuously from 1 to 1/ratio.
    d = saturation - threshold + half_knee
    return saturation + (1.0 / ratio - 1.0) * (d * d) / (2.0 * knee)
