# Provisional luminance response controls

This is an adjustable TEST candidate. Its final curve, ranges and visual acceptance remain open.

The original 27-control v3 candidate remains separate. This branch uses `parameters/press_machine_v3_curve.json` with 29 controls, plugin ID `com.46slv.PressMachine.v3.curve.dev` version 3.1, bundle `PressMachineV3CurveDev.ofx.bundle`, and DCTL `PressMachine_V3_Curve_TEST.dctl`. Existing nodes, projects, v2 artifacts, the original v3 schema and old generated DCTL are not migrated or overwritten.

## Two provisional adjustments

- **Luma Pivot EV**, default 0, trial range -6 to 6. Shifts the zero crossing from scene-linear Y 0.18 to 0.18 * 2^EV.
- **Luma Width**, default 1, trial range 0.25 to 4. Higher values keep the response near zero over a broader luminance range; lower values reach the shadow/highlight response sooner.

Set **Luma Split** away from zero to use these controls. Hue Angle still selects the direction, Hue Strength controls Pattern displacement, Hue Bias sets global attraction, and Luma Split controls signed attraction amount. The two additions change only the luminance axis. No extra saturation, contrast or tone-curve stage has been added. This symmetric family is a starting point, not an arbitrary-point curve editor.

## Isolated evaluation boundary

`core/press_machine/HueLumaCurve.dctlh` owns the existing response and prototype mapping. It receives the original immutable scene-linear `Y_ref`; it does not read post-Hue or post-Density luminance. Hue geometry, anchors, the fixed-input skin mask, Density math, protection domains and final desaturation remain separate.

For positive Y, let r = sqrt(0.18) * 2^(PivotEV / 2). Form q = (sqrt(Y) - r) / (sqrt(Y) + r), then q_adjusted = q / [Width + (1 - Width) * abs(q)]. Nonpositive Y remains -1. The default 0/1 pair calls the original q_ref function directly, preserving its arithmetic path. Invalid prototype settings fall back to the original response without disabling the rest of the pipeline. Changing the curve cannot affect output when Luma Split is zero.

The response is bounded and monotonic over the proposed positive Width range. It preserves the existing zero-Y reconstruction. Scaling the reference root avoids multiplying extreme HDR Y by exposure gain.

## Evidence for this candidate

See the JSON receipts in [`results/v3_curve`](../adapters/ofx/results/v3_curve):

- 75,877 focused shared-core/formula/generated-DCTL checks and 77 alpha/extreme cases passed.
- The new curve suite passed 14,450 checks. A separate local comparison added 1,200 old-adapter cases: 4,800 RGBA words were exact with the new curve at 0/1. This is a sampled compatibility result, not whole-domain equivalence.
- Windows MSVC/SDK build, NVRTC compilation, exports and package layout passed.
- The independent CUDA kernel and actual CUDA adapter each passed 20,100 pixel cases, including 8 nondefault curve states. Each changed 924 outputs relative to the default curve. Maximum CPU difference was 1.1920928955078125e-7. This used one NVIDIA context, positive pitch and small fixtures; later synchronization/readback does not establish independent asynchronous completion or product Host behavior.
- Resolve Studio 21.1.0.14 built-in DCTL displayed the 29-control candidate. Default readbacks matched the schema; Bypass was visually off. A synthetic 1152x384 frame was captured at default, Split100, Pivot2, Pivot2/Width3, active Comp, active Hue and Shadow Desat states. All 1,327,104 RGB values per frame met the comparison tolerance, with maximum CPU difference at most 8.940696716308594e-8, zero nonfinite values and word-exact alpha.
- Pivot2 and Width3 each changed the actual captured RGB output. Saving, closing and loading the owned test project preserved the combined state and reproduced an identical EXR file SHA. This was project reload, not a cold application restart or DRP import.
- Shadow Desat Threshold 0.5 / Knee 0.18 produced exactly equal output R, G and B for 217,496 chromatic input pixels classified safely below the full-desaturation boundary. This is a synthetic deep-region observation, not a boundary/knee or visual-quality oracle.

[`HOST_DCTL_LIMITED.json`](../adapters/ofx/results/v3_curve/HOST_DCTL_LIMITED.json) contains hashes, completed job IDs, actual adjustment deltas and the separate remaining gates. Existing v3 Host captures do not qualify this new candidate.

## Known Host limitation

After project reload, the DCTL name field displayed blank even though the parameter values and captured output persisted. Resetting only the DCTL-row list restored the displayed name without changing the active values. This is an observed workaround, not an established root cause or proof of cold-start behavior. Do not use the whole-effect reset to repair the name if you need to preserve adjustments.

Product OFX Host loading/persistence, all UI endpoints/menu operations, representative footage, 4K performance, cold application restart, PowerGrade/DRP import and final visual selection remain open. This candidate is not an accepted release.
