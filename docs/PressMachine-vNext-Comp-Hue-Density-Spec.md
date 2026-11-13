# Current product contract: Press Machine 2.2

This current override supersedes the historical29/27-control checkpoints and pipeline below where they conflict. The historical text is retained as evidence, not a request to remove subsequently approved controls.

- User-facing name: **Press Machine 2.2**. Existing trial compatibility keys stay `com.46slv.PressMachine.v3.curve.dev`, OFX major/minor3.1, internal bundle stem `PressMachineV3CurveDev`. Public2.2 is not an OFX major downgrade or replacement of released v2.
- Current schema:30 controls, with `pm_makeup` appended at index29,0..200/default100; earlier29 IDs/types/defaults/ranges/options/order preserved. Graph is a separate viewer-only switch.
- Current conditioning: raw Pre Sat -> raw Sat Comp -> raw Makeup Sat, then **one** original-input Comp Skin net mix for the whole block. Then Hue -> post-Hue Density -> **one** Look Skin net mix for the combined Hue+Density change -> Final shadow/highlight desaturation. Comp Skin is not a second Comp operation.
- Makeup inherits Pre's model. Neutral100 preserves the prior29-control result; there is no automatic v2 or27-control migration.
- Graph is mandatory in every OFX artifact: variable Pattern swatches, neutral-input Hue output-color-strength curve, four-panel auto1.5 with tiny-viewer fit limits; OpenFX overlays required. Reference curves are not footage measurements. SatComp curve is BASE COMP BEFORE MAKEUP, not the full conditioning response.
- Actual2.2 descriptor-only binary75799ec745badc5219909dd35afcf494a9a28fb304eed4bd7cbbd2319eb75251 keeps the tested Makeup core/schema/PTX/Graph. Source f1e78eb and later build/CI/evidence commits are not a new pixel formula.
- SS2.2 installation/label/Graph and existing-trial state recognition are complete within their recorded limits. Current generated DCTL ae50fc47726103e12041186a287c4f3ef0580c3074092c86993ecae7942121ca has limited actual built-in Host default/active evidence. Neither is full-domain acceptance.
- NonDensity-first remains the priority history; baseline Density integration may be inspected without declaring all nonDensity gates complete or adopting a new Hue formula. New mask expansion and research white-fringe/texture models are not adopted.

### Mandatory Graph build/package gate

Every current OFX product build must run the non-optional Graph source-structure gate before compiling the product target, including direct CMake builds. The normal build script and package verifier must also fail closed when Graph descriptor, overlay registration, draw path, redraw wiring or OpenGL linkage is missing. Generation remains a prerequisite; missing generated descriptors must fail, not silently disable Graph. This does not change pixel processing, Graph defaults or legacy v2 artifacts.

The package gate checks the current source tree, not the provenance or Graph contents of an arbitrary binary supplied to the verifier. Source/package structural checks are not proof of Host overlay visibility, viewport behavior or visual acceptance. Exact-binary Host evidence remains separately required. Negative mutation tests exercise missing Graph wiring and the actual mandatory CMake target dependency without claiming a portable fixture builds the Windows OFX product.

### Windows build generator selection

The normal build accepts optional `-Generator` for reproducible Visual Studio builds. Without it, preserve an existing CMake cache generator; for a fresh build, use CMake standard detection (including CMAKE_GENERATOR environment preference). Require a Visual Studio generator and x64 target. An explicit/environment generator conflicting with cache, a non-x64 cached platform, or an unsupported generator must fail before source generation; never delete or rewrite cache to resolve a conflict. Unavailable Visual Studio installations fail at CMake configure. Run in an x64 Visual Studio Developer shell for native-reference tests requiring cl.exe. VS2019 remains selectable explicitly when installed. No product behavior or Host acceptance changes.

### New-build Graph package binding

New product builds write `Contents/Resources/GRAPH_BUILD_BINDING.json` in a product-target POST_BUILD step after rerunning the mandatory source gate. Format version 1 binds the fixed product binary path and SHA256 to canonical-LF hashes of the listed Graph/build inputs, including generated descriptors and the verification scripts. Normal package verification requires this sidecar and exact current-source/binary agreement, and rejects missing, malformed, stale, incompatible-version or redirected-path records. If only a hashed non-compiler input changes and an incremental build does not relink, package verification fails closed; perform a clean product rebuild to produce a fresh binding. No automatic legacy bypass is provided. Existing released v2/v2.2.0 assets are unchanged; their historical receipts do not become new-build binding receipts.

This is accidental stale-build/binary-substitution detection, not signed provenance, proof that the compiler consumed the declared inputs, reproducible-build certification or proof of Graph execution. A party able to replace both the binary and sidecar can forge this binding. Real descriptor probing and exact-binary Host visibility remain separate open conditions. The implementation changes no product C++ or pixel formula. Portable compiled fixtures exercise POST_BUILD wiring but are not Windows OFX builds; a newly distributed binary still needs exact-binary Host smoke verification.

[日本語利用メモ](PressMachine-2.2-Quick-Guide-JA.md).

Current bounded receipts and open conditions: [2.2 gates](../adapters/ofx/PRODUCT22_GATES.md), [Density integration](../adapters/ofx/PRODUCT22_DENSITY_INTERACTION.md).

---

## Historical implementation specification

# Press Machine vNext — Comp → Hue → Density implementation specification

Status: **v3.dev base specification / provisional 29-control extension below / product OFX Host acceptance pending**
Date: 2026-11-09  
Scope: shared pixel core, parameter schema, DCTL and OFX adapters

This document defines the implementation contract for the next Press Machine color pipeline. It does not change or reinterpret the released v2.0 plugin, existing DCTL artifacts, saved nodes, or their acceptance receipts.

## Current 29-control candidate and contract clarification

The user requested an adjustable provisional luminance-to-hue response, then OFX packaging and release inclusion only if its tests pass. DEV-12 contract Revision 4 records non-Density completion first, Density follow-up afterward, and future mask expansion deferred. Existing Skin Protect and baseline Density integration remain regression obligations.

- Current candidate: [Draft PR #10](https://github.com/46slv/press-machine/pull/10), branch `dev/non-density-luma-curve-20261110`, implementation `7bdc4ba11246e926378ed7f17493931cebb185dc`, evidence/docs head `15d4a94c0d5e5743c46d29dcd889233782ae25fc` before this documentation-only clarification.
- The 27-control base is [Draft PR #9](https://github.com/46slv/press-machine/pull/9), `36c3cea889aefb4772274587fee7e2f12ba39ed4`. Both PRs remain unmerged at this checkpoint.
- The extension adds only `pm_luma_pivot_ev` and `pm_luma_width`. Its isolated mapping, defaults, invalid-value fallback and limited receipts are specified in [Provisional luminance response controls](PressMachine-Luma-Curve-Prototype.md). This candidate-specific extension supersedes the no-extra-curve-controls statements in section 7 for this variant only. It does not introduce a general tone/contrast stage or finalize the curve family/ranges.
- Standalone Windows CPU/CUDA, build/package/export checks and limited built-in Resolve DCTL captures are complete within their recorded scope. Product OFX load/render/UI/persistence, representative footage, full profile coverage, 4K and final visual/release acceptance remain open. See the exact receipts in [`results/v3_curve`](../adapters/ofx/results/v3_curve).
- DCTL SHA256: `8c9ebcb72295d60877f300d5ddb863d629b565cb0be11deb984e5f1b77bafad6`; OFX SHA256: `2661e8575f01a27e86f2c09af99fbb92d2aa0ff7655f9c490c391d5cccefb1a3`. A docs/evidence-only head does not constitute new whole-head Host acceptance.

The actual released v2.0.0 package has 25 controls and already includes Final Shadow and Highlight Desaturation. This 29-control candidate is the changed 27-control vNext pipeline plus two provisional controls, not v2 plus two compatible additions. Keep the separate plugin ID and existing v2 nodes; do not auto-convert old menu indices or saved states.

## Historical 27-control source/evidence checkpoint

- Source candidate: [Draft PR #9](https://github.com/46slv/press-machine/pull/9), head `53f074b12d3b05ad23fd830e152d6c89c8434787`.
- Focused CI: run `42599109654`, 75,877 checks PASS; generated DCTL↔CPU 180 mixed cases bit-exact; 600 profile selector combinations bit-exact/finite; alpha/extreme 77 PASS/max error 0; Windows harness static contracts PASS.
- Target Windows CUDA/OFX/Resolve, persistence, footage, 4K and final visual acceptance remain unverified.


The design goal is to make the responsibilities explicit:

- **Pre Saturation + Saturation Comp** condition the incoming chroma range.
- **Hue Pattern + Hue Bias + Luma Split** design the color distribution and therefore where Density will react.
- **Density** converts the post-Hue color distribution into weight, sinking or lift.
- **Final Shadow Desaturation** decides whether the finished look keeps color in deep black.
- Press Machine does **not** provide a general contrast or tone-curve stage.

---

## 1. Canonical pipeline

```text
Input profile decode / primary conversion
→ fixed input analysis: Y_ref + skin mask
→ Pre Saturation
→ Saturation Comp
→ Comp Skin Protect (one net-domain mix)
→ Hue Pattern
→ Hue Bias / Luma Split
→ post-Hue canonical saturation analysis
→ Density / Density Chroma / Shadow-Highlight Protect
→ Look Skin Protect (one net-domain mix)
→ Final Shadow Desaturation
→ output primary conversion / transfer encode
```

### 1.1 Stage responsibilities

| Domain | Responsibility | Must not do |
| --- | --- | --- |
| Conditioning | Pre Saturation and SatComp create a controlled chroma range before creative Hue processing | Create a split-tone look or global contrast |
| Hue / Look | Hue Pattern, Bias and Luma Split form hue topology and warm/cool distribution | Act as a hidden post-Hue saturation limiter or tone curve |
| Density | Read the actual post-Hue color and map its chroma distribution to weight | Read raw Hue slider values as a hidden multiplier |
| Final black policy | Optionally remove chroma from the finished deep shadows | Re-protect skin or modify global contrast |

Hue is not specified as a saturation booster. It may increase or decrease chroma as a consequence of moving color in the chroma plane. That result is intentional input to Density.

---

## 2. Parameter contract

Create a new versioned parameter schema instead of silently changing `press_machine_v2.json`. Existing plugin IDs and saved states are not migrated in place.

### 2.1 Conditioning

| ID suggestion | Label | Range / default | Meaning |
| --- | --- | --- | --- |
| `pm_pre` | Pre Saturation | existing range / 100 neutral | Chroma gain before Comp |
| `pm_threshold` | Threshold | existing range/default | SatComp threshold |
| `pm_compression` | Amount % | existing range/default | SatComp amount |
| `pm_softness` | Knee % | existing range/default | SatComp knee |
| `pm_sat_skin` | Comp Skin Protect | 0…100 / 0 | Protect the **net PreSat + Comp result** |

Keep the existing IDs where their meaning remains compatible. Only the user-facing label and application point of `pm_sat_skin` change.

### 2.2 Hue / Look

| ID suggestion | Label | Range / default | Meaning |
| --- | --- | --- | --- |
| `pm_hue_angle` | Hue Angle | 0…360° / existing default | Shared primary hue / phase for Pattern, Bias and Split |
| `pm_hue_pattern` | Hue Pattern | menu / Complementary | Pattern anchor family |
| `pm_hue_compression` | Hue Strength | 0…100 / 0 | Direct multiplier of the Pattern target displacement |
| `pm_hue_bias` | Hue Bias | -100…100 / 0 | Positive attracts globally toward Angle; negative toward Angle+180° |
| `pm_luma_split` | Luma Split | -300…300 / 0 | Positive sends highlights toward Angle and shadows toward Angle+180°; negative reverses it |

Accepted Pattern menu, in this order:

1. Mono
2. Analogous
3. Complementary
4. Split Complementary
5. Triadic
6. Tetradic

`Hue Bias` and `Luma Split` remain active when Hue Strength is 0. They are independent of Pattern Strength.

### 2.3 Density / Look protection

Keep the existing Density parameters and meanings. Rename the user-facing label of `pm_density_skin` to **Look Skin Protect**.

`Look Skin Protect` covers the net result of Hue + Density. It does not cover conditioning and does not apply to Final Shadow Desaturation.

### 2.4 Final desaturation

Keep the current Shadow Threshold / Knee contract. Threshold 0 remains exact off. For active Shadow Threshold > 0, positive Knee provides the smooth transition; Knee 0 intentionally keeps input at level >= Threshold and fully desaturates below it. Do not require smoothness across that supported hard-step endpoint.

Independent Final Highlight Threshold / Knee controls are already implemented in the released v2 package and current candidate. The R3 optional feature designation is not a claim of missing implementation and is not promoted to Must here. Because the controls are included, their off/default, active and overlapping Shadow/Highlight behavior still requires regression testing. Final desaturation is separate from Density Highlight Protect.

---

## 3. Fixed input analysis

Let `x0` be the common scene-linear working RGB after the input adapter.

Compute once, before creative stages:

```text
Y_ref  = working-space scene-linear luminance(x0)
M_skin = existing original-input skin mask(x0)
```

`Y_ref` and `M_skin` are immutable for the pixel throughout the pipeline.

- Luma Split reads only `Y_ref`.
- Skin protection uses only `M_skin`.
- PreSat, Comp, Hue and Density outputs must not move their own qualifier or skin mask.

This lets an upstream Resolve node establish contrast while preventing self-feedback inside Press Machine.

---

## 4. Conditioning domain

Use the current Pre Saturation and SatComp scalar/color cores. Do not rewrite the accepted Comp curve merely to accommodate the new ordering.

```text
x_pre_raw  = PreSat(x0, internal_skin_keep = 1)
x_comp_raw = SatComp(x_pre_raw, internal_skin_keep = 1)
```

Per-stage validity fallback:

```text
if x_pre_raw is invalid:  x_pre_raw  = x0
if x_comp_raw is invalid: x_comp_raw = x_pre_raw
```

Comp Skin coefficient:

```text
K_comp = 1 - (CompSkinProtect / 100) * M_skin
x_cond = x0 + K_comp * (x_comp_raw - x0)
```

Properties:

- Comp Skin 0: unprotected conditioning result.
- Comp Skin 100 at mask core: exact `x0` for the entire conditioning domain.
- Partial protection is applied once to the domain net delta, not once per stage.
- Comp’s no-boost, threshold, knee and continuity guarantees are evaluated between `x_pre_raw` and `x_comp_raw`, not against later Hue or Density output.

---

## 5. Hue working plane

Use the current fixed, Y-preserving two-dimensional opponent plane connected to linear BT.2020 / XYZ D65. Preserve the current accepted Angle phase calibration.

Let:

```text
v0 = opponent coordinates of x_cond
Yh = chosen linear Y of x_cond
phi = phase0 + radians(Hue Angle)
```

Hue Pattern, Hue Bias and Luma Split operate in this plane and reconstruct a single zero-Y color delta back into the working RGB. Do not perform separate RGB round trips for Pattern and Split.

For overflow resistance, normalize plane calculations with:

```text
scale = max(abs(v0.x), abs(v0.y))
```

Perform geometry on `v0 / scale`, then restore `scale`. Exact zero is handled explicitly. Finite negative and HDR values are not clamped to 0…1.

---

## 6. Hue Pattern target field

### 6.1 Anchor offsets

Offsets are relative to `phi`:

| Pattern | Anchor offsets |
| --- | --- |
| Mono | `{0°}` |
| Analogous | `{-30°, 0°, +30°}` |
| Complementary | `{0°, 180°}` |
| Split Complementary | `{0°, 150°, 210°}` |
| Triadic | `{0°, 120°, 240°}` |
| Tetradic | `{0°, 90°, 180°, 270°}` |

Angle is always the primary hue. Analogous uses Angle as its center. Tetradic uses the square form for the implementation baseline.

### 6.2 Mono

Mono uses the existing shifted-ray target so neutral gray may tint while Y remains fixed.

For target unit direction `u` and its zero-Y RGB direction `D(u)`:

```text
rho(Yh, u) = max(Yh, 0) / -min(D_R(u), D_G(u), D_B(u))
T_mono(v, Yh, u) = max(rho(Yh, u), dot(v, u)) * u
```

Then:

```text
v_pattern = v0 + s_pattern * (T_mono(v0, Yh, u) - v0)
s_pattern = HueStrength / 100
```

### 6.3 Multi-anchor Patterns

For two or more anchors, use one general non-uniform circular cell mapping. This avoids separate special-case semantics for complementary, triadic and asymmetric patterns.

1. Sort the wrapped anchor angles.
2. Assign input angle `h` to its nearest anchor `a_i` using circular distance.
3. Let `d` be the signed shortest angle from `a_i` to `h`.
4. Let `H` be half the circular gap to the neighboring anchor on the side of `d`.
5. Normalize distance:

```text
u = clamp(abs(d) / H, 0, 1)
```

Use fixed angular compression constant:

```text
m = 0.10
Den = (1 + m) / 2
F(u) = [m*u + (1-m)*(u^3 - 0.5*u^4)] / Den
Q(u) = u^2 * (3 - 2*u)
```

`F` is the normalized integral of a strictly positive derivative. It fixes the anchor and boundary and preserves angular order. `Q` smoothly reduces chroma toward the cell boundary.

Full Pattern target:

```text
h_target = a_i + sign(d) * H * F(u)
r_target = r * [1 - Q(u)]
T_pattern = r_target * unit(h_target)
```

Strength is a direct Cartesian displacement multiplier:

```text
v_pattern = v0 + s_pattern * (T_pattern - v0)
```

Consequences:

- Hue Strength 0 is exact identity.
- Anchor rays are fixed.
- At a cell boundary, the full target is neutral; both adjacent cells meet at the same coordinate.
- At Strength below 100, the boundary retains `(1-s_pattern)` of its input radius.
- No hard nearest-anchor output switch occurs.
- The same equation handles non-uniform Analogous and Split Complementary cells.

Tie-breaking at an exact midpoint may be deterministic by anchor index because both sides have the same mathematical boundary output. Float seam tests remain required.

---

## 7. Fixed Luma Split curve

The original 27-control Luma Split uses a broad, fixed scene-linear response around 18% gray. That base has no curve controls. The separately versioned 29-control TEST extension exposes provisional Luma Pivot EV and Luma Width only, as specified in [the prototype contract](PressMachine-Luma-Curve-Prototype.md). Defaults 0/1 call the original response directly. No general Knee, Toe, Shoulder, Gamma, Contrast or tone-pivot stage is added.

Let:

```text
sY  = sqrt(max(Y_ref, 0))
s18 = sqrt(0.18)
q_ref = (sY - s18) / (sY + s18)
```

For `Y_ref <= 0`, this naturally evaluates to `-1` when `sY=0`. The denominator is always positive.

Properties:

- `q_ref(0) = -1`
- `q_ref(0.18) = 0`
- `q_ref(0.72) = +1/3`  (about +2 stops)
- `q_ref(2.88) = +3/5`  (about +4 stops)
- Negative-stop values are symmetric in log exposure.
- The response approaches ±1 asymptotically and has no hard threshold.

This formula remains the 27-control baseline and the exact default path of the 29-control extension. The extension's two provisional adjustments alter only the luminance-to-hue weight and read the immutable original-input Y_ref. Reference images and hands-on use will inform later curve selection; the current family/ranges are not finally accepted.

---

## 8. Hue Bias and Luma Split drive

Normalize controls:

```text
B = HueBias / 100
S = LumaSplit / 100
r_drive = B + S * q_ref
```

Map the unbounded additive drive to a bounded, monotonic attraction weight:

```text
a = abs(r_drive)
e = exp2(2*a)
w = sign(r_drive) * (e - 1) / (e + 1)
```

Set `w=0` exactly when `r_drive=0`.

This is equivalent to `tanh(ln(2)*r_drive)` but avoids requiring a separate tanh implementation. With the allowed controls, `abs(r_drive) <= 4`, so `e <= 256`.

Pure Split, at `abs(q_ref)=1`:

| Luma Split | abs(w) |
| ---: | ---: |
| 25 | 0.171572875 |
| 50 | 0.333333333 |
| 100 | 0.600000000 |
| 200 | 0.882352941 |
| 300 | 0.969230769 |

Combined Bias + Split extreme reaches `255/257 ≈ 0.992218`, still without overshoot.

Target rays use the same shifted-ray function as Mono:

```text
T_plus  = T_mono(v_pattern, Yh, unit(phi))
T_minus = T_mono(v_pattern, Yh, unit(phi + PI))

v_hue = v_pattern
      + max( w, 0) * (T_plus  - v_pattern)
      + max(-w, 0) * (T_minus - v_pattern)
```

Properties:

- Bias positive attracts toward Angle; negative toward Angle+180°.
- Split positive sends highlights toward Angle and shadows toward Angle+180°.
- Pattern Strength may be 0 while Bias/Split remain active.
- `abs(w)<1`, so the result never overshoots the selected ray target.
- Neutral gray may tint when Bias or Split is active.
- Pattern + Bias + Split reconstruct to RGB once, preserving the chosen Hue-stage Y within numerical tolerance.

---

## 9. Post-Hue Density analysis

Density must read the actual `x_hue`, never Hue Strength, Bias, Split, Pattern index or 2D displacement length.

Reuse the current v2.0 Density canonical response and domain conditioning on the post-Hue sample. Do not invent a second saturation metric unless the existing implementation fails the explicit domain tests.

Current response contract:

1. Peak-normalize the post-Hue signed RGB.
2. Convert the normalized sample through the existing signed-root Oklab path.
3. Let `C = hypot(a,b)` and valid `L > 0`.
4. Define:

```text
q = 4*C/L
p = SaturationResponse  // 1…4
W_sat = q^p / (1 + q^p)
```

Use the existing reciprocal branch for `q>1` to avoid overflow.

Multiply by the existing smooth domain confidence `W_domain`:

```text
W_density = W_sat * W_domain
```

Required behavior:

- Neutral is exactly 0.
- At `C/L = 0.25`, response is 0.5 for every `p`.
- Response is monotonic in chroma.
- Increasing `p` suppresses low chroma and concentrates Density on high chroma.
- Signed wide-gamut channels remain eligible when the existing domain is valid.
- Invalid/nonpositive Density domain makes Density a local no-op; the valid Hue result is retained.

Keep the current Density amount semantics:

```text
max_stop = 4.5 * W_density
DeltaE = -(Density / 300) * max_stop * ToneKeep
```

Therefore approximately:

- Density ±100: up to ±1.5 stops before tone protection.
- Density ±300: up to ±4.5 stops before tone protection.

Keep the current Density Chroma and Shadow/Highlight Protect equations unless focused tests reveal a separate bug. Their input tap changes to post-Hue.

---

## 10. Look domain and skin protection

Run Hue and Density internally without repeated skin attenuation:

```text
x_hue = HueLook(x_cond, Y_ref, internal_skin_keep = 1)

if DensityBypass:
    x_density_raw = x_hue
else:
    x_density_raw = Density(x_hue, internal_skin_keep = 1,
                            ShadowProtect, HighlightProtect, ...)
```

Per-stage validity fallback:

```text
if x_hue is invalid:         x_hue = x_cond
if x_density_raw is invalid: x_density_raw = x_hue
```

Look Skin coefficient:

```text
K_look = 1 - (LookSkinProtect / 100) * M_skin
x_look = x_cond + K_look * (x_density_raw - x_cond)
```

Properties:

- Look Skin 0: full Hue + Density result.
- Look Skin 100 at mask core: exact conditioned color; Hue and Density are both protected.
- Hue→Density interaction is calculated before protection, then attenuated once as one look.
- Density Bypass bypasses only Density. Hue remains and is still controlled by Look Skin Protect.
- Density Shadow/Highlight Protect remain internal tone controls and are not replacements for skin protection.

---

## 11. Final Shadow Desaturation

Apply the existing final desaturation to `x_look` after Look Skin Protect.

```text
x_final = FinalShadowDesat(x_look)
```

Contract:

- Shadow Threshold 0 is exact off.
- When active, classification reads the actual post-Hue/post-Density image.
- Deep shadows may be driven smoothly to neutral even if Luma Split previously colored them.
- Skin protection is not applied again.
- The chosen linear Y is preserved within the existing final-stage tolerance.
- This stage is a creative final-black policy, not an error guard.

Interpretation:

- OFF: preserve colored blacks created by split tone and Density.
- ON: neutralize the selected deep-black range after the look is complete.

---

## 12. Pipeline state and fallback order

Refactor the shared stage snapshot so its semantic order matches the new pipeline. Suggested fields:

```text
input
pre_raw
conditioned
hue
look
final
```

Raw diagnostic intermediates may be recorded separately, but output fallback must not expose an unprotected raw skin branch.

Output conversion fallback order:

```text
final
→ look
→ hue
→ conditioned
→ input
```

Rules:

- An invalid stage preserves the latest valid previous stage and later valid stages may still run where meaningful.
- Density failure must not erase a valid Hue result.
- Hue failure must not erase valid conditioning.
- No creative-stage error rolls the pixel all the way back to encoded input unless all later valid candidates fail output conversion.
- Output conversion is still performed when creative controls are neutral but input/output profiles differ.

---

## 13. Fast paths and identity

Update the gray and neutral fast paths.

Do not skip Hue for gray when any of these is active:

```text
Hue Strength != 0
Hue Bias != 0
Luma Split != 0
```

Bias/Split may intentionally tint gray for every Pattern.

Global creative identity requires all creative stages neutral:

```text
PreSat neutral
Comp Amount 0
Hue Strength 0
Hue Bias 0
Luma Split 0
Density 0 or Density Bypass
Final Desaturation off
```

Profile conversion remains separate from creative identity.

RGBA contract remains unchanged:

- Preserve alpha.
- Evaluate premultiplied nonzero-alpha RGB straight, then premultiply again.
- Retain hidden RGB for zero alpha.

---

## 14. Source change map

### `parameters/`

- Add a new versioned schema, for example `press_machine_vnext.json`.
- Replace Points menu with Pattern menu in the new plugin schema.
- Add Hue Bias and Luma Split.
- Relabel `pm_sat_skin` to Comp Skin Protect.
- Relabel `pm_density_skin` to Look Skin Protect.
- Order groups by actual processing order.

### `core/press_machine/PixelMath.dctlh`

- Split input analysis from stage application: return fixed `Y_ref` and raw `M_skin`.
- Run PreSat and Comp with internal skin keep 1; apply one Comp-domain mix.
- Replace the point-count-only topology dispatcher with the Pattern anchor table and general cell target field.
- Fuse Pattern + Bias + Split into one opponent-plane conversion/reconstruction.
- Reuse current post-color `pmvq_response` and Density domain helpers on `x_hue`.
- Run Density with internal skin keep 1; apply one Look-domain mix.
- Keep final desaturation last.
- Update stage snapshot and output fallback order.

### `core/press_machine/PixelPipeline.dctlh`

- Add Pattern, Hue Bias and Luma Split parameters.
- Update gray/identity fast paths.
- Pass fixed analysis and new stage order to the shared core.

### adapters

- Regenerate DCTL and CPU/CUDA shared headers from the same core.
- Use a new DCTL filename and OFX identifier/version.
- Do not reinterpret old Points values or old saved control positions.

---

## 15. Required tests

### 15.1 Scalar tests

- `q_ref`: exact values at 0 and 0.18, monotonicity, finite HDR behavior.
- Bias/Split `w`: odd, monotonic, exact 0, table values above, `abs(w)<1` for all UI values.
- Pattern `F`: `F(0)=0`, `F(1)=1`, strictly positive derivative.
- Pattern `Q`: endpoints 0/1 and monotonicity.
- Strength 0 exact identity and direct displacement scaling.

### 15.2 Pattern geometry

For every Pattern, Angle seam and Strength `{0,25,50,75,100}`:

- anchor rays fixed;
- XY/RGB continuity at every cell boundary;
- no negative angular ordering step for non-neutral output;
- deterministic exact midpoint behavior;
- gray behavior;
- opposite-color behavior;
- scale covariance across low chroma, normal and HDR magnitude;
- no NaN/Inf for finite input.

### 15.3 Protection domains

For Comp Skin and Look Skin `{0,50,100}`:

- each net delta is applied once;
- no squared/double protection response;
- Look Skin 100 preserves conditioning while bypassing both Hue and Density on mask core;
- Comp Skin changes do not alter Hue/Density formulas outside their changed input;
- Density Bypass leaves Hue intact.

### 15.4 Hue→Density interface

- post-Hue neutral gives Density weight 0;
- fixed Y/hue chroma sweep gives monotonic Density weight;
- Pattern/Bias/Split do not feed Density via raw controls;
- high-chroma and nominal-gamut crossings remain continuous;
- invalid Density domain retains valid Hue output;
- Density ±100 and ±300 preserve current amount semantics;
- Density Chroma four quadrants keep their existing meanings.

### 15.5 Final black policy

Use one strong split-tone scene with Final Shadow Desat off/on:

- off preserves colored deep shadows;
- on smoothly neutralizes only the configured range;
- no skin re-protection;
- Threshold 0 exact identity;
- no boundary banding or flicker on a moving gradient.

### 15.5.1 Final Shadow/Highlight source regression contract

The existing final-stage controls retain their current semantics. Both masks classify
`DI(Y(x_look))` once, with linear DWG Y coefficients (0.27411851, 0.87363190,
−0.14775041). Their chroma keeps multiply: `x_final = Y + (x_look − Y) *
shadow_keep * highlight_keep`. Do not sequentially reclassify the already desaturated
output or apply skin protection again. Positive knees use cubic smoothstep over
`[max(0, shadow_threshold − shadow_knee), shadow_threshold]` and
`[highlight_threshold, min(1, highlight_threshold + highlight_knee)]` respectively.
Shadow threshold 0 and highlight threshold 1 disable their respective masks.
Zero knees intentionally hard-switch outside the threshold, preserving chroma at the
threshold itself; continuity is required only for positive-width knees.

The focused source regression covers overlapping and separated masks, clipped knees,
DI toe/log transition and HDR/negative luminance, exact default identity, neutral
preservation, invalid-control local fallback, and final-stage placement after the
protected look. Finite nonpositive Y neutralizes only with an active shadow mask.
All four controls must be finite and in [0,1] for an active final stage; an invalid
control bypasses this stage without discarding the look. This supplements existing
requirements, not a new creative model. Highlight remains Should/Candidate, not
a new Must. Older artifact Host results are not inherited by the current binary. Binary64 independent equations are compared
with the shared float-pair core; mixed active controls also compare the CPU adapter
with CPU-compiled generated DCTL. This does not certify Resolve, CUDA, temporal
perception, alpha transport or broad footage acceptance.

### 15.6 End-to-end / Host

- CPU reference → generated DCTL → OFX CPU → OFX CUDA parity, tied to exact source hash.
- Resolve compile/load and all new controls.
- UI range/default/menu readback.
- save/reopen and PowerGrade reuse.
- representative footage: neutral chart, skin and dark skin, red/cyan opposition, foliage, sky, neon, night, HDR, finite negative and extreme saturation.
- 4K playback and slider response under the same cache/timeline conditions.
- alpha, output-profile conversion and fallback behavior.

---

## 16. Implementation slices

### Slice A — shared CPU core

Done when:

- new schema is parsed;
- fixed analysis, Comp-domain mix, Pattern field, Bias/Split mapping, post-Hue Density and Look-domain mix are implemented;
- focused scalar/geometry/domain tests pass;
- all neutral controls preserve the previous neutral core result.

### Slice B — generated DCTL

Done when:

- the generated DCTL compiles in target Resolve;
- all controls display and persist;
- CPU/DCTL numeric fixtures pass;
- representative stills verify the intended Comp→Hue→Density behavior.

### Slice C — OFX

Done when:

- CPU and CUDA consume the same new parameter snapshot and pixel core;
- parity and render-window/alpha tests pass;
- the new plugin identifier coexists with v2.0.

### Slice D — product acceptance

Done when:

- visual acceptance confirms useful low/mid control and intentionally extreme upper ranges;
- Final Shadow Desaturation behaves as the explicit colored-black choice;
- same-condition 4K use is practical;
- exact artifact hashes, installation notes and known limits are recorded.

---

## 17. Non-goals and migration

- No general contrast, pivot, toe, shoulder, black-point or white-point controls.
- No hidden gamut mapping or post-Hue saturation limiter.
- No automatic migration of v2.0 nodes, Points values or artifacts.
- No claim that extreme Hue remains inside Rec.709 or another display gamut.
- No claim that hard-clipped information can be reconstructed.
- No spatial, temporal, semantic face-mask or multi-image processing in this change.

The v2.0 release and its immutable evidence remain separate. This specification is complete enough to begin source implementation without additional product decisions; remaining choices are implementation constants, focused verification, and visual acceptance rather than architecture questions.

## 18. v3.dev source qualification receipt — 2026-11-09

Implemented in the separate 27-control schema and `com.46slv.PressMachine.v3.dev` identity:

- Comp-before-Hue pipeline with one original-input skin analysis and fixed `Y_ref`.
- One net Comp Skin mix and one net Look Skin mix, including protected output fallback.
- Six Pattern families, common skin-reference Angle, direct Strength, independent Bias and Split.
- General non-uniform Pattern field, one zero-Y reconstruction, and the existing post-Hue Density response.
- Schema-generated CPU/CUDA parameter snapshot, OFX descriptors, DCTL controls and default values.
- Final black policy and exact neutral conditioning/Density paths. New Bias/Split gray coloration is not bypassed.

Focused Linux/GCC checks (`tests/verify_vnext.py`): **74,077 checks passed**. Independent binary64 formula comparison covers the scalar mapping, all Pattern fields, anchor/cell boundaries, angular order, phase seam, scale covariance, direct Strength, fixed input reference, both protection domains and post-Hue Density tap. Maximum scalar absolute error: `1.4544e-14`; geometry absolute error: `7.1475e-12`; normalized Hue Y error: `1.0053e-14`. The CPU-compiled generated DCTL and the CPU adapter are bit-exact for 180 mixed states. Invalid controls are isolated to the affected stage: valid later stages continue, and Density failure keeps the valid Hue result. The 77-case alpha/extreme fixture passed with maximum error 0. Exact generated hashes are in `adapters/ofx/SOURCE_MANIFEST_V3.json`, with focused receipts under `results/v3/`.

These are source/CPU checks, not a Resolve DCTL compiler receipt or a native OFX binary receipt. Old v2 schema, DCTL and evidence remain unchanged. Do not use the old 25-value harness against the new 27-value ABI.

Still unverified: Windows SDK/NVRTC build, CUDA kernel/adapter execution, Resolve UI/default/menu readback, save/reopen and PowerGrade persistence, completed-frame CPU/CUDA/DCTL comparisons, representative footage, same-condition 4K responsiveness, HDR/negative/gamut visual behavior, and final user acceptance. Analogous is fixed at ±30° for this candidate: its compact 60° outer span remains distinct from the characteristic 90° Tetradic and 120° Triadic spacing, while stronger Primary-Hue dominance remains the independent Hue Bias responsibility. ±45°/±60° are no longer pre-implementation gates; reopen the offset only if footage/Host evidence shows a material Analogous usability problem. Density redesign research is a separate candidate and is not silently integrated here.

Host work must continue through the single assigned Resolve owner after the higher-priority Density work. This candidate is not an accepted release or permission to replace v2 in existing projects.

## 2026-11-13: owner-requested Rec.709 input primaries

Owner request: add709 to the input gamut menu. Append `Rec.709 D65` to Input Primaries as index4; retain old indices0..3, defaults, parameter IDs/count/order, plugin ID and Graph. Rec.709 means primaries/white only, not a new transfer function or display transform. Input Transfer stays independently selected; do not silently select gamma2.4/sRGB/BT.709 OETF or reinterpret existing projects.

Convert scene-linear Rec.709 D65 to the existing scene-linear DWG core using chromaticity-derived matrices, and provide the inverse for Output Primaries `Same as Input`. No new explicit output-gamut choice is requested. Default same-profile fully neutral processing must preserve encoded RGB exactly under the existing identity policy; old choices must retain bit-exact processing. New709 state should not be saved over with an older build which lacks that choice.

Scope: schema/descriptors, shared CPU/CUDA/DCTL core, focused independent matrix/roundtrip/active/neutral and old-profile regression tests. This amendment does not change Density/Hue math, adopt a final Hue operator, claim Host acceptance, or authorize replacing installed bundles before separate preservation/recognition checks. Existing709 gamma-encoded footage still needs a matching transfer setting or upstream linearization; present transfers do not include gamma2.4/sRGB/BT.709 OETF.

## 2026-11-13 01:53:39 UTC: owner-authorized display-profile completion and main

This later owner instruction supersedes the input-only scope above: choose suitable709-related gamuts/gammas, validate without relying on the owner to detect mathematical errors, and integrate to main by the normal protected workflow. Preserve existing IDs/defaults/indices/30-value ABI/Graph and released v2 artifacts.

Append input Rec.2020 D65(index5), P3 D65(index6) after Rec.709 D65(index4). Append explicit output Rec.709 D65(index5), Rec.2020 D65(index6), P3 D65(index7) after old choices0..4. Use invertible chromaticity-derived D65 matrices to/from scene-linear DWG, without adaptation or gamut mapping/clipping. P3 D65 is not DCI P3 cinema white.

Append input transfer Gamma2.4(index5), Gamma2.2(index6), sRGB(index7), Rec.709 OETF(index8), output indices6..9 respectively. Existing Same/transfer indices retained. Gamma decode=sign(v)*abs(v)^g; encode exponent1/g. Gamma2.4 is ideal zero-black power, not a nonzero-black BT.1886 display model. sRGB uses .04045/.0031308 knees,12.92 slope,1.055/.055,exponent2.4. Rec.709 OETF uses continuous alpha1.09929682680944,beta.018053968510807,slope4.5,exponent.45 with matched inverse, avoiding the tiny gap in rounded1.099/.018 constants. Extend new transfers oddly for negative values; no range rescale, implicit transfer selection, tone mapping or0..1 clamp. Unrepresentable finite cases follow existing fallback; neutral same-profile encoded identity stays exact.

Pairings:709+Gamma2.4 for correctly described display-referred graded709;709+sRGB for sRGB;P3D65+sRGB for Display P3;709+Rec709OETF for that OETF-encoded signal. These describe actual node input/output, not automatic display rendering or original-camera metadata. PQ/HLG and absolute-HDR/OOTF/black-offset policy are outside this SDR amendment.

Acceptance: independent rational matrix/analytic transfer oracle at0/toes/knees/1/negative/HDR/overflow; active conversions/OutputSame; old profiles word-exact; CPU/generatedDCTL/CUDA parity and append-only schema; Windows Host representative709Gamma2.4 and DisplayP3/sRGB or2020, saved-state/legacy/pixel/Graph checks with restored environment; final CI and normal main integration without protection bypass. No broad perceptual/material/HDR acceptance implied.
