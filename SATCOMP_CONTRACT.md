# SatComp — High-Saturation Compressor Contract (prebuild)

## Product definition

SatComp is a saturation compressor specialized for reducing only high-saturation colors.
It is not a generic saturation knob and it is not a gamut mapper.

The operator is split into two independent layers:

1. **Color / saturation model** — convert the host input into a canonical representation, measure saturation on a fixed reference, and reconstruct the color.
2. **Scalar transfer** — map `S_in -> S_out` with Threshold / Ratio / Knee.

Keeping these layers separate prevents input encoding or gamut size from silently changing the artistic control law.

## Scalar transfer v1

Parameters:

- `Threshold >= 0`: center of the compression knee.
- `Ratio >= 1`: compression ratio above the knee. `1` is exact identity.
- `Knee >= 0`: width of the smooth transition. `0` is hard-knee.

For `Knee = 0`:

```text
S <= Threshold : S_out = S
S >  Threshold : S_out = Threshold + (S - Threshold) / Ratio
```

For `Knee > 0`, a quadratic soft knee is used. It is continuous in value and first derivative at both knee boundaries.

Deliberate v1 decisions:

- no implicit `0..1` clamp;
- no implicit saturation ceiling;
- no saturation boost when `Ratio >= 1`;
- monotonic transfer;
- `Ratio = 1` is exact bypass.

A ceiling/limiter, if added later, is a separate stage and must not be hidden inside this transfer.

## Color-management contract

Target pipeline:

```text
host/input encoding
  -> decode transfer exactly once
  -> convert primaries/white point into canonical color representation
  -> measure S_in on a fixed saturation reference
  -> scalar SatComp transfer
  -> reconstruct color while preserving chosen Lightness + Hue invariants
  -> convert to requested output primaries/white point
  -> encode output transfer exactly once
```

Required invariants:

- The same physical/tristimulus color encoded as Rec.709, DWG/Intermediate, ACES-family input, etc. must produce equivalent SatComp decisions within numerical tolerance.
- Saturation normalization must not depend on the size of the *input* gamut.
- Alpha is unchanged. If the host buffer is premultiplied and a nonlinear color transform is required, unpremultiply/re-premultiply around color processing.
- Negative RGB and RGB > 1 are not silently clipped.
- Gamut mapping/clipping is a separate explicit policy.
- Neutral colors remain neutral.
- Below the untouched region (`Threshold - Knee/2`), the complete operator must be identity within tolerance.

## Acceptance gates

### Scalar transfer — cloud/unit-testable now

- exact identity for Ratio=1;
- exact identity below hard threshold;
- correct requested slope `1/Ratio` in the compressed region;
- C1 continuity across soft-knee edges;
- monotonicity;
- never boosts saturation for Ratio>=1;
- no hidden ceiling.

### Color model — next implementation slice

Use deterministic tristimulus/color vectors and verify:

- cross-encoding invariance for equivalent colors;
- neutral-axis identity;
- hue preservation tolerance;
- lightness preservation tolerance;
- finite output (no NaN/Inf);
- negative/>1 preservation policy;
- alpha invariance;
- explicit out-of-gamut behavior.

### Resolve/DCTL host gate

Only after the repository implementation is pinned to an exact commit:

- DCTL compiles/loads in the target Resolve version;
- identity/below-threshold images are visually and numerically unchanged;
- high-saturation patches compress as predicted by the scalar oracle;
- no unexpected clipping on scene-referred/extended-range material;
- input/output color-space modes match the canonical test vectors.

## Canonical saturation model candidate — implemented oracle

The prebuild now includes a concrete candidate designed to satisfy encoding/gamut invariance:

```text
input encoding
 -> linear RGB in declared primaries
 -> XYZ at the source white point
 -> Bradford adaptation to D65 when required
 -> Oklab / OkLCh
 -> S = C / L
 -> Threshold / Ratio / Knee transfer
 -> C_out = S_out * L
 -> preserve Oklab L and hue
 -> inverse path
```

Why this candidate is useful:

- Oklab is device-independent once the input is correctly converted to D65-relative XYZ.
- `C/L` is an Oklab saturation definition and is invariant to positive exposure scaling because Oklab `L` and `C` scale together under uniform XYZ scaling.
- The scalar can exceed 1, so there is no hidden assumption that saturation is a clamped `0..1` quantity.
- A small black floor makes near-black chroma noise ineligible for compression instead of turning division by a tiny `L` into a large selector.

This remains a **candidate until image/Resolve evaluation**. The mathematical oracle is implemented so it can be compared against alternatives (for example pure Oklab chroma, Okhsl-style normalized saturation, or a fixed-reference gamut-relative metric) using the same image corpus before the public parameter meaning is frozen.

Current reference colorimetry includes:

- Rec.709/sRGB primaries (D65)
- Rec.2020 primaries (D65)
- DaVinci Wide Gamut primaries (D65)
- ACEScg/AP1 (ACES white -> Bradford D65)
- sRGB transfer reference
- Rec.709 OETF reference
- DaVinci Intermediate encode/decode
- ACEScct encode/decode

PQ/HLG are intentionally not treated as a context-free `gamma` toggle: their luminance/system semantics must be part of the explicit ColorContract before implementation.
