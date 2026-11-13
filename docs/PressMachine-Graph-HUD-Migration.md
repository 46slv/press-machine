# Graph HUD reuse: 29-control source candidate

This migrates the existing HUD from `33c72a8b8d25a5bad8355aa2f27594cec5939c8e` onto the 29-control curve candidate `c0f475565f5d4cd82e8e23f6dee575b6fe930a49`. It is a source candidate, not a released or Host-qualified binary. It does not redesign Density, Split, or masks.

## Reused implementation and display contract

The original bitmap alphabet, OpenGL state preservation, translucent panels, viewport/RoD placement, plotting primitives, OpenGL V1 registration and unconsumed pen/key defaults are reused. Graph remains an OFX-only, nonanimated checkbox, defaults OFF, and requests no image evaluation on change. It is not part of the 29 processing values, `pm::Parameters`, DCTL, CPU pixel processing, identity checks or CUDA. The plugin identifier/version and bundle name remain the current v3 Curve TEST candidate's.

The Hue panel is taller to show the existing candidate's controls. Its Pattern swatches use `pmvn_pattern_count` and `pmvn_anchor`, including the nonuniform Analogous and Split Complementary spacing. They are direction keys at a display gamut boundary, not predicted output colors. Zero retains the skin-reference phase. Strength replaces the obsolete COMP label. The labels also show Bias, Split, Pivot EV and Width.

Two separate lines plot original-input reference luminance from -6 to +6 EV, with 0 EV = 0.18 Y:

- **Q** is the actual `pmvn_curve_q_ref(Y_ref, pivot, width)` response, in [-1, +1].
- **Drive** is `pmvn_drive(Bias, Split, Q)`, the signed attraction toward Angle/opposite, in [-1, +1]. It is not a final hue angle. Pattern and protection can change the final output direction. Current provisional Split behavior is preserved.

The original Compression base transfer and Final Sat Keep plots retain their meanings. Neither is a footage measurement.

Density keeps the existing fixed Skin/Red/Blue reference probes, 33 exposure samples per probe, EV and relative Oklab C/L plots, auto ranges, and gaps for undefined chroma ratios. It now uses the current `pmvn_process` mapping. Both endpoints use the same original-input Look protection: protected Hue → protected Look. Conditioned → Look would include Hue and is not displayed as Density-only. Consequently Density bypass or Density zero yields a flat contribution even with active Pattern, Bias, Split and Look protection. IO encodings do not apply to already-linear DWG reference probes; Final Desaturation is outside these endpoints.

All 29 current schema handles are generated into redraw slave registration. Both snapshot arrays use `kParameterCount`; changing any value invalidates the model, while unchanged redraws reuse it. Nonfinite snapshots are rejected without poisoning the cache. A rebuild performs 99 Density stage evaluations plus bounded curve sampling; it never fetches image pixels or reads the GPU. The larger panel raises the viewport minimum from 400×230 to 400×308 pixels; smaller viewports skip the HUD. Visible-image fitting retains the original scale behavior with the revised height.

## Reproduce source checks

Use a checkout with the pinned c0f4755 baseline commit available. Run from the repository root:

```sh
python adapters/ofx/regenerate.py
python adapters/ofx/generate_descriptors.py
python adapters/ofx/tests/verify_hud.py
```

The portable runner compiles the models with g++ on Linux or an initialized MSVC shell on Windows. It does **not** compile the OFX overlay against the SDK. Receipts are isolated under `adapters/ofx/results/v3_curve/graph/`. The Windows build script additionally links OpenGL and runs the same model/source gates after the full OFX build. CI includes the portable tests on Linux and Windows; local passing tests are not a remote CI result.

Focused coverage includes all six Patterns and known anchor angles, independent scalar Q/Drive references, exact helper mapping, every cache slot, invalid/repeated cache inputs, zero-knee boundaries, compression, skin protection, Density interactions, graph/model nonmutation, and 1,000 before/after pixel comparisons. Source separation pins the canonical LF content of 16 immutable files and confirms that the Processor and ImageEffect classes, plugin identity, shared-core hash and generated DCTL hash are unchanged. The old CPU/GPU/Host matrix is not rerun or relabelled as new evidence.

## Remaining acceptance and safe handoff

No Windows SDK build, OFX installation, Resolve interaction, render or export was performed in this migration lane. An independent source review found no remaining blocking issue, but is not SDK or Host evidence.

Before installation, the sole Host owner must resolve previous work ownership and inspect existing 4K export receipts rather than repeat an uncertain job. Build this exact source in a separate output tree, record its module/PTX hashes, and coordinate any swap of the existing TEST candidate. Preserve projects, render queue, unsaved work and installed artifacts. This source lane did not alter another writer's checkout.

The exact built binary still needs:

1. Native Windows SDK compile/link, package checks and provenance.
2. Graph off/on visibility, all-control redraw including Pattern/Bias/Split/Pivot/Width, zoom/RoD/viewport fitting, and unobstructed normal interaction.
3. Saved-state/reopen behavior for Graph and the 29 processing controls.
4. Graph off/on completed-frame exact equality, confirming no export burn-in.
5. Bounded changed-control and unchanged-redraw operation/performance on the target Host. Cloud model timings are not Resolve performance.

Do not call this installed, released, or fully accepted until those gates are recorded for the actual binary.
