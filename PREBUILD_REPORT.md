# SatComp vNext — Prebuild Report

Date: 2026-08-31
Status: `CANONICAL_REPO_BRANCH_READY` / Resolve host validation pending

## Goal implemented

Rebuild SatComp around one narrow product purpose:

> Reduce only saturation above a numeric threshold, with predictable `S_in -> S_out` behavior, while making color-space/transfer handling explicit and independently testable.

Current artistic controls:

- Threshold
- Ratio
- Knee
- Bypass Compression

No v1 Ceiling control and no implicit saturation/gamut clipping.

## Implemented vertical slice

### Scalar compressor

- hard-knee and C1-continuous soft-knee transfer;
- exact `Ratio = 1` identity;
- identity below the untouched region;
- monotonic;
- cannot increase saturation when `Ratio >= 1`;
- no hidden ceiling.

### Color model / CPU oracle

Canonical path:

```text
encoded RGB
 -> declared transfer decode
 -> declared gamut/white -> XYZ D65
 -> Oklab
 -> S = C/L
 -> Threshold / Ratio / Knee
 -> preserve Oklab L + hue, reduce C
 -> XYZ D65
 -> declared output gamut
 -> declared output transfer
```

Implemented standard combinations:

- Rec.709 / linear
- sRGB
- Rec.709 OETF
- Rec.709 primaries / Gamma 2.4
- Rec.2020 / linear
- DaVinci Wide Gamut / linear
- DaVinci Wide Gamut / DaVinci Intermediate
- ACEScg / linear AP1
- ACEScct / AP1

The DCTL exposes primaries and transfer separately so the transform contract is explicit. PQ/HLG are intentionally deferred until their luminance/system semantics are represented instead of being reduced to context-free gamma switches.

### DCTL candidate

`SatComp_vNext.dctl` includes:

- explicit input/output gamut and transfer;
- DWG/DI and ACEScg/ACEScct conversions;
- ACES-white -> D65 adaptation for Oklab measurement;
- Oklab forward/inverse math;
- high-saturation compression only;
- exact same-encoding fast paths to avoid below-threshold round-trip drift;
- no `_clampf` / `_saturatef` gamut clipping;
- numerical finite-output guard.

`Bypass Compression` bypasses the compressor only. If a different output encoding is explicitly selected, the declared colorimetric conversion still runs.

## Verification actually run

Command:

```text
python validate_prebuild.py
```

Result:

- Python/unittest: **33/33 PASS**.
- DCTL native parity harness: PASS.
  - DCTL itself is compiled into a native shared object for the test.
  - standard supported input encodings are compared against the CPU oracle;
  - standard input/output encoding pairs are cross-compared against the CPU oracle;
  - exact identity fast path is checked for float bit preservation at the harness boundary.
- standalone `clang -std=c11 -fsyntax-only` DCTL smoke check: PASS.

This validation catches transfer/matrix/Oklab/DCTL implementation drift, but it does **not** prove that Resolve's DCTL compiler/runtime accepts every construct or that host buffer semantics match our declared contract.

## Current design confidence

High confidence:

- Threshold / Ratio / Knee transfer semantics.
- no-boost / monotonic / soft-knee properties.
- separation of color encoding from compressor law.
- deterministic CPU oracle and DCTL numerical parity under the prebuild harness.

Candidate, not frozen:

- Oklab `S=C/L` as the public meaning of numeric saturation.
- default Threshold scale/value, which should be tuned against real image material after the metric is accepted.

## Remaining Resolve-only gates

1. Pin the exact task-branch commit in `46slv/press-machine`.
2. Load/compile the DCTL in the target Resolve 21 build.
3. Verify what RGB/transfer/state the DCTL receives in the actual placement in the grading pipeline; do not infer it from project UI labels.
4. Apply deterministic patches/vectors and compare Resolve output against `SATCOMP_TEST_VECTORS.csv` / CPU oracle.
5. Verify alpha behavior and any premultiplied-alpha boundary relevant to the chosen ResolveFX/DCTL path.
6. Test negative and >1 scene-referred values for unexpected host clipping.
7. Image QA on skin, neon/LED, saturated red/blue, gamut-edge colors and near-black chroma noise.
8. Compare `S=C/L` against at least pure Oklab chroma or another candidate only if image QA exposes a concrete weakness; do not broaden the design speculatively.

## Repository state

Canonical repository is now resolved as `46slv/press-machine`. The repository was empty when imported, so this validated vertical slice becomes the first implementation lane. Resolve host acceptance remains pending and must be tied to the exact branch/commit SHA used for the test.

## Learning Gate

Result: `CAPTURED_OR_MECHANIZED`.

The reusable validation delta from this work is mechanized in `tests/dctl_syntax_shim.h`, `tests/dctl_runtime_harness.c`, `tests/test_dctl_runtime_parity.py`, and `validate_prebuild.py`: static C syntax alone is not treated as sufficient; the DCTL code is also executed in a native harness and compared numerically to the CPU oracle before host testing.
