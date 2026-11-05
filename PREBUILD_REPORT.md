# DEV-12 R2 prebuild result — 2026-11-05

The bounded R4/R5 slice passes its focused reference/native checks, with the
two epsilon-boundary observations below retained. This is not Resolve, visual
or full DEV-12 acceptance. Source revision is the local commit containing this
report, on `dev/dev12-r2-dwg-di-20261105`, based on canonical main
`a926635f52411fcd15486790008d38169fcea623`.

DCTL SHA256: `35442c75a7b31c6da0bfe94dfa8cbb6b3ab13737752bb81a36afa28ed2b671b8`.
Machine-readable evidence: `evidence/measurement.json`, `parity_budget.json`,
`prebuild.json`, `fixture_readback.json`. They pin DCTL/vector hashes, commands,
compiler, dimensions, counts and numeric maxima. No legacy/A2 files were ported.

## Exact commands and results

Run from repository root, Python 3.12.10, Windows 11 build 26200:

```powershell
python -m unittest discover -s tests -v
python tools/build_native.py
python tools/qualify.py
python tools/qualify.py --check
python tools/host_fixture.py
python tools/check_fixture.py
git diff --check
```

The standalone build was used during setup; `qualify.py` also builds the native
shim. Existing VS2019 Community MSVC 19.29.30137 x64 is used with `/std:c++17 /O2 /fp:strict
/EHsc /W4`. Four C4100 warnings are the required RGB entry point's unused image
coordinates/dimensions. No dependency was installed. FFmpeg is used only for
independent EXR decoding; it is not required for scalar/native qualification.

| Check | Result |
|---|---|
| Independent reference/source unittest suite | 11 tests PASS |
| Native scalar mappings / boundary neighbors | 180,280 samples PASS |
| Native scalar exact identity | 43,324 bit-preserving returns |
| Native scalar monotonic / no boost | 0 decreases / 0 boosts |
| Native RGB vs double oracle | 336 color/control cases; 115 oracle-compressed |
| Native RGB exact identity | 219 bit-preserving returns; 2 guard crossings below |
| Finite-bit RGB stress | 253 cases, 0 new nonfinite outputs |
| Direct L/C/S epsilon/nonfinite domain tests | 24 PASS |
| Native DI/signed-root anchors | 8 PASS |
| Nonfinite bypass payload/sign preservation | 2 PASS |
| Independent authored EXR readback | 8 files, 114,688 float words bit-exact |

Reference tests cover official DI anchors/branch inequalities, DWG primary-derived
matrix agreement, signed-root Oklab roundtrip, positive exposure invariance,
L/h/chroma reconstruction, extended range and exact identity. Scalar C1 is
checked analytically at both endpoints. Reference color roundtrip tolerances
derive from printed matrix residual and the cube-root derivative bound, rather
than demanding that rounded published inverse matrices be exact inverses.

## Measured error and frozen envelope

| Quantity | Observed maximum | Frozen normalized limit |
|---|---:|---:|
| Scalar absolute / normalized error | 8.544921883e-6 / 8.264210465e-8 | 1.192092896e-7 |
| Encoded RGB absolute / normalized error | 6.187159905e-5 / 6.187159905e-5 | 1.220703125e-4 |
| DI/root anchor normalized error | 3.234607863e-7 | 4.768371582e-7 |

Normalized error is absolute error divided by max(1, absolute reference value),
or max(1, maximum absolute reference channel) for RGB. Each frozen limit is
`2**ceil(log2(measured_max))`: the next binary boundary above measured error,
less than twice that error. Limits were computed after measurement and frozen
before host access. Exact identity paths have zero tolerance. This empirical
envelope applies to the recorded fixtures; it is not an analytic universal GPU
bound or automatic permission to widen a host failure's tolerance.

Worst scalar case: S=140.375/T100/C25/P100, reference 128.059287109375,
native 128.05929565429688.

Worst RGB case: `S250.0_h4.0/hard_zero`, input encoded
(.507253885269165, .48451170325279236, .7186648845672607).
Reference output (.19883946876635858, .36711007997409123, .46798792247974585);
native (.19890134036540985, .36711710691452026, .4679955542087555).
Its double LMS x is -2.212096397e-5, near a cancellation zero. Cube root
magnifies conversion rounding: double Lab L=.4999807875, a=-.8172344246;
native L=.5000081658, a=-.8169777989. This sensitivity is an explicit R6/R7
wide-gamut metric risk; no hidden clamp, weighting or alternative curve is added.

Double C=9.990367548e-8 is native C=1.000007614e-7 for the near-neutral
`C_guard_9.99e-08` patch. It crosses the guard in strong and hard_zero states;
their RGB differences from oracle identity are 7.1054e-15 and 1.9860e-12.
These cases remain in RGB error measurement and are separately reported,
not counted among bit-exact identities. Direct Lab/S tests prove equality
returns identity at binary32 guard constants and eligibility immediately above.

## Repaired attempts and remaining stages

- First reference run: 9/11 passed. Two test assumptions were repaired: the
  official DI table's linear40 rounding discrepancy, and a very saturated DWG
  blue whose negative Oklab L correctly requires identity. Active blue and
  invalid-domain blue are now tested separately. The formula was not changed.
- First native build failed on cmd/Python embedded-quote escaping, before any
  native test executed. A generated local .cmd fixes toolchain setup quoting.
- Initial native measurement rejected the two epsilon-boundary differences.
  Diagnosis exposed native Lab and retained both differences explicitly;
  the DCTL's approved epsilon and curve were not altered.
- Final focused checks pass. Current failures: none in the executed stages.
- NOT RUN: target Resolve UI/compile/load, GPU/oracle parity, actual host
  negative/HDR and alpha behavior, 4K interactivity, representative visual/user
  acceptance, integration/install/smoke. No stage is replaced by A2 evidence.

No push, PR, merge, release, installation, Resolve or GUI mutation occurred.
Main, the separate old checkout and legacy/A2 branch heads remain preserved.
Exact runtime model identity is not exposed by this environment; `gpt-6.1-sol`
could not be independently verified. No substitute model/worker was selected.
