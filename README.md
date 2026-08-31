# SatComp vNext prebuild checkpoint

Canonical implementation branch for `46slv/press-machine`. This repository starts from the SatComp vNext vertical slice prepared and validated on 2026-08-31.

## Product direction

SatComp is a **high-saturation compressor**, not a generic saturation knob:

- low/mid saturation remains untouched;
- high saturation is controlled numerically by `Threshold / Ratio / Knee`;
- no hidden saturation ceiling;
- no hidden `0..1` gamut clamp;
- color-space/transfer conversion is a separate explicit layer;
- the current saturation metric candidate is Oklab `S = C/L`, preserving Oklab lightness and hue while reducing chroma.

The Oklab metric is still a candidate until Resolve/image evaluation; the transfer-function contract is already fixed and independently testable.

## Files

- `SatComp_vNext.dctl` — DCTL candidate with explicit input/output gamut + transfer controls.
- `satcomp_transfer.py` — scalar `S_in -> S_out` CPU oracle.
- `color_model.py` — colorimetry/transfer/Oklab CPU oracle.
- `SATCOMP_CONTRACT.md` — product, color and acceptance contract.
- `SATCOMP_TEST_VECTORS.csv` — deterministic host-validation vectors.
- `generate_vectors.py` — regenerates the vectors.
- `tests/test_satcomp_transfer.py` — compression-curve invariants.
- `tests/test_color_model.py` — color-space and transfer invariants.
- `tests/test_dctl_contract.py` — DCTL static contract checks.
- `tests/test_dctl_runtime_parity.py` — compiles the DCTL into a native harness and compares it numerically with the CPU oracle.
- `tests/dctl_syntax_shim.h` / `tests/dctl_runtime_harness.c` — native DCTL validation harness.
- `validate_prebuild.py` — one-command validation.
- `PREBUILD_REPORT.md` — current evidence and remaining host gates.

## Validate

```bash
python validate_prebuild.py
```

Current cloud/prebuild evidence: **33/33 tests PASS** and standalone Clang DCTL syntax smoke check PASS.
This is not a DaVinci Resolve runtime certification.

## Repository status

Canonical repository: `46slv/press-machine`. The Python/native validation gates are checked before merge. DaVinci Resolve host validation remains a separate gate and must be recorded against an exact Git commit.
