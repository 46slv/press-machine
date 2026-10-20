# Legacy v1.2.2 neutral Density correction

Local development candidate, based on accepted commit
`430aa1528c55abedfc6328cec6873432a374f27d` from
`fix/press-machine-legacy-v1-2-1`. The v1.2.1 directory and archived v1.1/v1.2
files are preserved unchanged. This is not a published release or host-certified
DCTL.

## Problem and expected behavior

In both v1.2 and v1.2.1, Dynamic Density uses `sat_pre`; Sat Density uses
`sat_out` after compression and Makeup. With UI Threshold `0.25`, Knee `0.1`
and Ratio `4`, the legacy knee blends toward `Threshold^3 = 0.015625` even
at zero input. It reports `sat_out = 0.005996346474` with Makeup `1`.

Reconstruction intentionally emits zero chroma when `sat_in <= 1e-6`, but
Sat Density still used this positive curve output to attenuate luma. With
Sat Density `1`, Density Compensation `0`, Dynamic Density `0`, Luma Mix `0`,
and input Y `0.18`, a neutral was darkened to `0.177866896920`.

The existing reconstruction guard is the maintenance contract used here:
Density must not react to saturation that reconstruction discards. The
guard is also retained explicitly in `docs/MIGRATION_NOTES.md`, section 2.
`legacy/v1.2.1/FIX_RECORD.md` preserves the creative response. The new core
design excludes legacy Density and redesigns compression; its proposed knee
formula is not a legacy maintenance specification.

## Minimal change

Only the new variant's Sat Density input changes:

```text
sat_for_density = sat_in > 1e-6 ? sat_out : 0
attenuation = 1 / (1 + sat_for_density * Sat_Density * 2)
```

This uses the same original-input guard as reconstruction, including when
Pre-Saturation or Makeup boosts tiny input chroma. The compressor output itself
is unchanged. Dynamic Density continues to use `sat_pre`. Luma Density and
Luma Mix `0..2` extrapolation remain intentional, so this is not a universal
grayscale bypass when those controls are active.

Outside the version/provenance header, the DCTL differs from v1.2.1 only by
the guarded variable and its use in the Sat Density attenuation expression.
The test enforces that complete payload comparison. Encodings, LogC4 toe and
roundtrip fixes, graph baseline, signed decomposition, reconstruction, creative
response above the guard, and Gamut Limit behavior are retained.

## Arithmetic evidence

The following source-executed scalar probes use the neutral reproduction
settings above. Python double arithmetic is shown; these are not GPU results.

| Input chroma length | v1.2.1 curve output | v1.2.1 Y | v1.2.2 Y | v1.2.2 chroma length |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.005996346474 | 0.177866896920 | 0.180000000000 | 0 |
| 0.0000005 | 0.005996711752 | 0.177866768518 | 0.180000000000 | 0 |
| 0.000001 | 0.005997077027 | 0.177866640117 | 0.180000000000 | 0 |
| 0.0000010001 | 0.005997077100 | 0.177866640092 | 0.177866640092 | 0.005997077100 |

## Verification

Run from the repository root:

```powershell
python -B -m unittest discover -s "Press Machine/legacy/v1.2.1/tests" -v
python -B -m unittest discover -s "Press Machine/legacy/v1.2.2/tests" -v
```

- v1.2.1 baseline: 5 tests passed.
- Unfixed v1.2.2 copy: the 7-method suite reported 8 failing assertions/subtests,
  including the neutral and inclusive small-chroma regression plus the missing
  source guard. No-op, nearby nonneutral and retained v1.2.1 contracts passed.
- Corrected copy: 7 tests passed. One test additionally runs all 5 existing
  v1.2.1 contracts against the new variant's source.

The harness translates only the actual scalar DCTL statements between
Pre-Saturation and recombination; it does not substitute a new compressor
formula. Chroma is represented by its magnitude because the block only scales
the original vector or replaces it with zero. Unsupported statements fail the
harness. Encodings use the retained arithmetic/source contracts, not host tests.

## Remaining limitation

The legacy knee still has a positive floor when its lower edge is below zero.
Immediately above the reconstruction guard, chroma jumps from zero to roughly
`0.006`. The Density guard now also makes Y step from `0.18` to approximately
`0.177866640092` at this boundary. Low nonzero chroma above the guard, including
nonneutral input with Pre-Saturation zero, can still receive artificial chroma
and Density attenuation from the legacy knee. This fix covers neutral and
near-neutral input only through the existing reconstruction guard.

A continuous response across that boundary requires deciding how to change the
legacy curve or reconstruction policy. No new knee, taper, subtraction or
near-neutral protection range is assumed here. The graph continues to display
the unchanged scalar compressor curve, including its floor. GPU precision,
DCTL compilation, Resolve rendering and visual acceptability remain unverified.
R2 DEV12/DWG-DI-to-Oklab, skin protection, gamut mapping and broader negative/HDR
policy are separate work. No push, PR, merge, release, installation or Resolve
operation was performed.
