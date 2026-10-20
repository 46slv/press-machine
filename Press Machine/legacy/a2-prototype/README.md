# Press Machine Legacy A2 Prototype

Approved A2 prototype 1, dated 2026-10-20. The candidate is
[`press_machine_a2_prototype.dctl`](press_machine_a2_prototype.dctl).
It is an isolated legacy experiment, ready for source review and user testing.
GPU compilation and Resolve behavior have not been verified.

The design basis is the A2 proposal at commit
`7e1870cc5a2690d72f37653b39c899c5e6a284b0`, approved for prototyping by the
user's “そうして” response. All earlier versions, the v1.2.2 partial candidate,
and the original proposal remain unchanged. This is a knee design change,
not a released v1.2.3. Model requested `gpt-6.1-sol`; runtime ID **UNVERIFIED**.

## Open the package

Extract the ZIP with its folders intact. The candidate file is at:

```text
Press Machine/legacy/a2-prototype/press_machine_a2_prototype.dctl
```

The older DCTLs included in the package are source fixtures for comparison and
tests. The candidate has the distinct header name `Press Machine Legacy A2
Prototype`; its filename also distinguishes it from those fixtures.

Choose the legacy Input Color Space matching the signal supplied to this DCTL.
The existing DWG, LogC3, LogC4, ACEScct and Linear mappings are unchanged.
For the numerical patch cases supplied here, use **Linear**. Do not treat the
Linear arithmetic values below as Log code values.

## Expected visible change

The old knee could generate approximately `.006` saturation from zero and
near-zero input. v1.2.2 hid that value from Density below `sat_in=1e-6`, leaving
a sharp chroma/luma step just above the guard. A2 removes the knee intercept
and reconstructs chroma with an analytic finite gain, without that hard discard.

It deliberately retains some legacy low-saturation lift. In the affected lower
knee, gain approaches at most `1.5`, while output chroma still tends to zero.
It does not adopt the alternative that forbids all saturation expansion.

The raw knee changes only for `Ratio>1`, `0<T<k`, and `0<=sat_pre<T`, where
`T=Threshold^3` and `k=max(Knee,1e-6)`. The existing Threshold mapping,
logarithmic Ratio mapping and Knee half-width are retained. At the reproduction
settings `Threshold=.25`, `Knee=.1`, the changed raw region is `sat_pre<.015625`.
For `Pre_Saturation=P>0`, this means original chroma length `sat_in<T/P`.
Pre-Saturation zero now produces zero chroma instead of a synthetic knee floor.

Reconstruction has a separate numeric change at every setting: legitimate tiny
chroma previously discarded at `0<sat_in<=1e-6` is retained and drives Density
continuously. Algebraically equivalent gain expressions can round differently
from older versions even outside the changed knee. Bit-identical output is not
promised. See [CHANGE_RECORD.md](CHANGE_RECORD.md) for source details.

## Reproduction preset and later host review

For the supplied Linear patch cases, set:

| Control | Value |
| --- | ---: |
| Input Color Space | Linear |
| Pre-Saturation / Sat Boost | 1 |
| Dynamic Density | 0 |
| Threshold | .25 |
| Ratio | 4 |
| Knee | .1 |
| Makeup | 1 |
| Luma Mix | 0 |
| Sat Density Mix | 1 |
| Sat Dens Comp | 0 |
| post-Density Sat Boost | 0 |
| Gamut Soft Limit | 0 |
| Show Sat-Comp Curve | off for pixel comparisons |

[`LINEAR_PATCHES.csv`](LINEAR_PATCHES.csv) includes input RGB, expected scalar
and RGB outputs from the actual-source arithmetic harness, and per-row control
overrides. Other controls use the preset above. These are double-precision
reference values, not GPU captures. The patch chroma direction is orthogonal
to the existing Rec.709 luma weights, so its intended Y is `.18`.

For later user-controlled host assessment, compare a neutral ramp and a dense
near-neutral ramp across the former `1e-6` boundary, then the `.005` lower-knee
case and an unchanged `.03` case. Check the graph separately: it uses the same
gain helper, with the existing input axis `0..2` and output normalization `/2`.
It continues to plot the compression-plus-Makeup scalar curve, without adding
Pre-Saturation or the later Density Sat Boost to its axis meaning.

No host assessment, installation or Resolve operation was performed for this
package. Visual acceptance remains open.

## Run the focused arithmetic tests

Python 3 standard library is sufficient. From the extracted package root:

```powershell
python -B -m unittest discover -s "Press Machine/legacy/a2-prototype/tests" -v
```

Result from development: **12 tests passed**, including all five retained
v1.2.1 LogC4/graph contracts against this candidate. The suite executes the
actual helper and scalar transform statements. It covers zero/near-zero,
analytical branch and Threshold boundaries, the old guard step, Ratio one,
Pre-Saturation/Makeup zero, ordinary legacy behavior, source scope and graph
consistency. Binary32 edge probes round individual scalar operations.
See [TEST_RESULTS.txt](TEST_RESULTS.txt) for evidence and fingerprints.

## Numerical and policy limits

- Binary32 probes do not emulate GPU fused operations, approximate intrinsics
  or denormal flushing. The bounded gain removes the tiny norm division, but
  real host rounding of luma, chroma length and very small values is unverified.
- The gain bound is mathematical: up to `1.5` before Pre-Saturation/Makeup,
  and up to `36` with their existing UI maxima and the later saturation boost.
  It is not a promise against overflow in arbitrary extreme RGB inputs.
- The existing Threshold kink in the first derivative is preserved. A2
  preserves the value and left slope there; it is not a globally C1 knee.
- The existing Ratio-one gate, Luma Mix `0..2` extrapolation, signed-luma
  decomposition, luma zero-floor, encodings and optional Gamut Limit are
  retained. Ratio one alone is not a universal bypass when Density or other
  creative controls are enabled.
- There is no R2 port, skin protection or new RGB clamp/gamut policy.

The package is a private prototype for review and testing. No release, public
push, PR, merge or security change was performed.
