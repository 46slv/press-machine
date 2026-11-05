# Bounded source correction — 2026-11-05

Two minimal source repairs follow d3964ac9dba7a1e8e8787ec67b55a8d2b876f43f.
Branch remains `dev/dev12-r2-dwg-di-20261105`. The new source and all measured
reports are bound by DCTL SHA256
`1a679a3a8fd4a3cca5d93a1fd61f995ed44d6befa3b2aa4fc1e188aaa9eea438`.
The final local commit is recorded in the delivery RESULT; measurement metadata
records the parent commit plus exact working-source hashes to avoid a self-hash.

The canonical float3 entry signature is now one physical line, with the brace
on its own following line. [SDK provenance](NATIVE_ENTRY_PROVENANCE.md) records
official file hashes and the literal regression. This addresses a plausible
line-sensitive parser issue exposed by d3964ac's native validation failure.
The new source has not been passed through Resolve native validation or GPU
compilation; a C++ compile cannot prove this host issue is repaired.

In `pm_transfer`, `q=(100-compression)/100` replaces evaluation of `1-a` in the
hard/high tail. `a=compression/100` and the knee polynomial are unchanged.
This is algebraically the same approved transfer with better conditioning
near 100% compression. The four controls, guards, color model, exact identity
paths and product contract are unchanged. No projection, clamp, new weighting
or alternate knee is added.

## Executed focused checks

Existing Python 3.12.10, Windows 11 build 26200, MSVC 19.29.30137 x64.
Compile flags: `/std:c++17 /O2 /fp:strict /EHsc /W4`. Four C4100 warnings are
the required entry's unused image dimensions/coordinates. No tool was installed.

```powershell
python -m unittest discover -s tests -v
python tools/scalar_measure.py --output-dir evidence/repair-20261105
git diff --check
```

All 13 unit tests passed: the original 11 plus the literal SDK entry/brace
regression and an actual-DCTL native scalar regression. The new measurement
command compiles actual source, runs the original qualification code against
the frozen budget, and writes fresh reports without changing historical ones.
The two new corpora are measured once, independently of the original suite.

| Original corpus check | Current result |
| --- | --- |
| Scalar | 180,280; 43,324 exact identities; 0 decreases/boosts |
| RGB/control cases | 336; 115 oracle-compressed; 219 exact identities |
| Other native checks | 253 finite stress, 24 direct domain, 8 transfer/root, 2 nonfinite bypass payload cases pass |
| Scalar max normalized error | 8.264210465400577e-8, unchanged |
| RGB max normalized error | 6.187159905127193e-5, unchanged |
| Guard crossings | Same two named C-guard cases, maximum RGB difference 1.986e-12 |

All original scalar/RGB/conversion budgets pass unchanged. `PREBUILD_REPORT.md`
and `evidence/measurement.json`, `prebuild.json`, `fixture_readback.json`,
`parity_budget.json` remain byte-for-byte historical files. The authored vectors
and all eight original host EXRs are unchanged. The external R6 evidence and
old A2 source/deployment were not modified.

## Regression and its separate bound

Float32 inputs S500, T0.800000011920929, C99.69999694824219, P59.5:

| Result | Value |
| --- | ---: |
| Original native, reproduced before editing | 2.2976105213165283 |
| Independent unchanged double oracle | 2.29761524626017 |
| Conditioned native | 2.2976152896881104 |
| Original absolute error | 4.724943641676305e-6 |
| Conditioned absolute error | 4.342794035494535e-8 |
| Case-only absolute bound | 5.477947476871242e-7 |

For this positive high-tail case, `100-C` is exact by Sterbenz's lemma. Four
operations round: q division, S-T, multiplication and addition. With binary32
unit roundoff u=2^-24, gamma4=4u/(1-4u). The case bound is
`gamma4*abs(oracle) + 8*ulp_double(S)`; the last term conservatively covers the
unchanged double oracle's own evaluation. The original result fails this bound,
and the conditioned result passes. It is neither an expanded corpus envelope
nor a change to `evidence/parity_budget.json`.

## Reproducible expanded measurements

`tools/scalar_measure.py` and `evidence/repair-20261105/metadata.json` pin the
actual DCTL, oracle, generator, native harness, build script and executable
hashes, platform, compiler identity, flags and compile script. Exact controls
and float words are in `expanded_controls.jsonl`; worst cases and case-order
SHA256 values are in each report. Reports normalize error as
`abs(native-oracle)/max(1,abs(oracle))`.

Expanded neighbor corpus uses `random.Random(120220261106)`: 12,000 states
draw T from randrange(0,2001)/10 and C/P from randrange(0,1001)/10, each rounded
to float32; then 80 Cartesian edge states T=(0,.1,.2,199.9,200), C/P=(0,.1,99.9,100).
lo/hi follow the native float32 operation order. Per state, sample 0,500 and
the +/-5 representable float neighbors of lo,T,hi; nonnegative word indices
start at zero; deduplicate and sort within the state. This fixture restriction
does not add a clamp to the product. It gives exactly 421,486 samples, with
409,406 consecutive-sample comparisons across 12,080 states.

High-tail corpus uses float32 T=(0,.1,.8,1,25,134.5,199.9,200), all 1,001 UI
tenths C=0..100, P=(0,20,59.5,100), S=(500,1000,1e4,1e7,1e10,1e20,1e30,F32_MAX).
No deduplication: 256,256 samples across 32,032 states.

| Corpus | Max normalized error | Local decreases | Max absolute decrease | Nonfinite / boosts / negatives / C0 identity failures |
| --- | ---: | ---: | ---: | --- |
| Expanded neighbors | 1.780754835689492e-7 | 943 | 3.0517578125e-5 | 0 / 0 / 0 / 0 |
| Bounded high tail | 2.0360922633961318e-7 | 0 | 0 | 0 / 0 / 0 / 0 |

Expanded maximum absolute pointwise error is 6.362829208228504e-5. Its worst
normalized point is S246.67294311523438/T134.5/C91.0999984741211/P83.4000015258789:
native144.48336791992188, oracle144.48339364887207. One maximum-drop example
at T171.8000030517578/C100/P47.79999923706055 has adjacent S253.9203338623047
and253.92034912109375 produce171.80001831054688 and171.79998779296875.
The absolute drop is 3.0517578125e-5 (two output float steps at this magnitude).
High-tail worst normalized point: S1e7/T134.5/C15.100000381469727/P0,
native8490022, oracle8490020.271353541. At huge S, high-tail maximum absolute
error is 2.9571753062493203e31; normalized error is the meaningful scale here.

Parent-provided independent GCC measurements match these conditioned maxima
and counts. Its d3964ac expanded baseline had max normalized2.056455557e-6,
936 decreases, 0 boosts/negatives. That expanded baseline was not redundantly
rerun here. The changed decrease count is not classified as an analytic-law fix
or regression; floating evaluation order changes which adjacent pairs decrease.

The approved analytic law remains monotone. Pointwise float error and strict
adjacent-float monotonicity are separate: the new corpus contains counterexamples
to strict float-output monotonicity. Both expanded maxima exceed the original
fixture-derived 2^-23 scalar envelope. No expanded empirical envelope has been
adopted and the original budget is unchanged. These are bounded measurements,
not proof for every valid UI/input value or a full R5/R6 PASS.

## Remaining gates

New-candidate native validation and Color Page load/GPU compile, same-path
identity, applied-host numeric/extended-range/alpha checks, CST sandwich,
representative 4K performance and user visual acceptance remain unexecuted.
Near-zero LMS sensitivity and guard crossings remain explicit. See the
[current host handoff](REPAIR_HOST_HANDOFF.md). No GUI, Resolve console, restart,
staging, install, public push, PR, merge or release occurred in this correction.
