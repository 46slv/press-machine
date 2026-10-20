# Press Machine legacy v1.2.1 fix record

This is a repaired copy of the legacy v1.2 DCTL, based on commit `75a9fbfbe0f8cfb328257f27dda3ec0eb8d3f936` and original blob `50f92292b9d2fdf7c69ed4e71a5c1c22fe301b9a`. The archived v1.1 and v1.2 files are unchanged. This legacy lineage is separate from SatComp vNext / Oklab and from the newer Press Machine core specification.

## Changes

- Replaced only the LogC4 decode/encode pair with the ARRI LogC4 scene-referred reference equations, including the linear toe for encoded values below zero and linear values below the cut point.
- Corrected only the graph identity guide from `gy = gx * 0.5` to `gy = gx`. The curve x-axis spans `[0, 2]`; its displayed y coordinate is divided by two, so the normalized identity is `gy = gx`.

The saturation compression formula, Threshold mapping, Ratio mapping, Knee behavior, Makeup, low-saturation gain in the soft-knee region, signed-luma decomposition, luma zero-floor, and luma weights are unchanged.

## Verification

Run the dependency-free arithmetic and source-contract tests with:

```powershell
python -B -m unittest discover -s "Press Machine/legacy/v1.2.1/tests" -v
```

The ARRI 18% gray anchor is linear `0.18` ↔ LogC4 code `0.2783958365`; the tests also cover zero, negative toe values, `1.0`, and round trips. The graph test checks the normalized identity-line expression. The v1.2 arithmetic probe failed the 18% gray round trip (`0.18` encoded to about `0.16166` and decoded to `-0.0532`); v1.2.1 passes the reference-equation tests.

These checks do not compile the DCTL. Compilation and visual behavior in DaVinci Resolve remain unverified.

Reference: [ARRI LogC4 specification](https://www.arri.com/resource/blob/278790/dc29f7399c1dc9553d329e27f1409a89/2022-05-arri-logc4-specification-data.pdf).
