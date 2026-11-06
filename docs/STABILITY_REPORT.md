# Scalar stability and the blue-domain boundary

## Status and separation

This development branch contains an R2-compatible scalar precision repair in
`dctl/PressMachine_R2.dctl` and an **isolated, unapproved product-domain proposal**
in `prototypes/PressMachine_ContinuousDomain.dctl`. Neither was installed or run
in Resolve by this task. The approved R2 brief, original checkout and installed
DCTLs were not changed. This is not a usable-version or visual-acceptance claim.

Base: `37e0c2ed447e1218dae94ccd6ac7c4aef28eab72`.

- Baseline DCTL SHA256: `1a679a3a8fd4a3cca5d93a1fd61f995ed44d6befa3b2aa4fc1e188aaa9eea438`.
- R2 scalar repair SHA256: `b703789d8346a44ed6139cc66835d6a38e0affd96287e2ea043532b14abe1e55`.
- Isolated continuous-domain proposal SHA256: `f019e39ed6e5b928c2f05acb5c2586ff82527dcad66bc9112e0c41465da1d401`.

## Confirmed cause of the recorded blue jump

The existing host chart was linear DWG, not a chart in Rec.709 primaries. It
mixes .18 neutral with each pure DWG primary/secondary in 1024 steps, at peaks
.01, .1, 1 and 4. At peak 1, the recorded blue pair x2737 -> x2738 corresponds to
local ramp offsets 689 -> 690, T25/C75/P20:

- Input RGB approximately (.05876833,.05876833,.73227761) ->
  (.05859238,.05859238,.73307918).
- Independent double Oklab L: +.0008762051 -> -.0082241285.
- R2 output linear blue: .01157759 -> .73307915, delta .72150156.
- The second sample takes the **mandated L<=1e-6 original-RGB identity path**;
  the first is compressed. Native execution of the actual DCTL and the
  independent oracle both reproduce it. It is not a GPU-only finding.

The host observed delta .7215015292 in
`D:/Documents/Codex/PressMachine-AR3-20261107/synthetic-chart/comparison.json`.
The offline result differs only in expected conversion/float rounding. The
host chart and control settings are documented in that folder's fixture.json
and its parent's CHECKPOINT.md. Existing C0/Bypass 262144-word identity is a
separate result and does not test this compression-domain transition.

Changing the epsilon alone cannot solve the structural problem: identity on
one side of zero and nonzero compression on the other have different limits.
Removing that transition requires a product-domain revision. It is not an
ordinary implementation correction to the approved R2 guard.

## R2 scalar repair, without a contract change

The subtractive knee evaluation had 943 local decreases in the existing seeded
fractional/adjacent-float corpus. The repaired scalar computes the same
piecewise polynomial with compensated binary32 pairs. Explicit `_fmaf` retains
product residuals; the installed Resolve 21.1 SDK README documents `_fmaf` at
line 318, float2/make_float2 at lines 42-43. No double type, clamp, saturation
ceiling, hidden weighting, new control, matrix, identity guard or oracle change
was added to the R2 DCTL.

Both independent Linux GCC 14.2 and Windows MSVC 19.29 strict-FP execution of
the actual sources measured the same results:

- Original 180280 scalar samples and existing RGB/domain/finite suites pass the
  **unchanged** frozen scalar/RGB/conversion budgets and exact identities.
- Expanded 421486 samples / 12080 states: local decreases 943 -> 0; maximum
  normalized scalar error 1.78075e-7 -> 5.94223e-8.
- High tail 256256 samples: local decreases 0; maximum normalized error
  2.03609e-7 -> 5.95814e-8.
- These measured errors are below the existing scalar 2^-23 budget. It was not
  widened. These sampled results are not a universal proof over all float inputs
  or evidence for a GPU compiler's arithmetic behavior.
- Original worst RGB error stays 6.18716e-5, within 1.220703125e-4. Existing two
  C-guard rounding crossings remain recorded, not hidden by epsilon changes.

The focused suite includes the old regression pair, full expanded/tail corpora,
exact control identities, the recorded blue pair and separate proposal tests.
See `evidence/stability-20261107/{tests-final.log,scalar,domain-probe.json}`.

## Isolated domain proposal and its tradeoff

Proposal: extend public S to `100*C/abs(L)` for nonzero signed L. At L=0 use the
continuous infinite-S limit. Compute in chroma units to avoid division by L:

- center chroma = T*abs(L)/100; half knee = center*Softness/100.
- Low region remains exact input identity.
- High-region C_out = (1-A)*C + A*T*abs(L)/100.
- Knee uses the same quadratic expressed in chroma units.
- Signed Oklab L and hue are retained; C_out<=C, exposure invariance, four
  controls, C0/Bypass, finite handling, no RGB clamp and no gamut map remain.
- The R2 L<=1e-6 and S<=1e-7 exception policy is intentionally changed. The C
  neutral guard remains. **This proposal has not replaced the approved brief.**

Measured comparisons:

- Recorded peak-1 C75 pair blue delta .72150156 -> .00084226.
- 12540 signed-L/chroma/control direct cases: finite, no boost or negative scale;
  scale absolute error <=2.97937e-8 against independent double reference.
- 276 positive-L pixel vectors: maximum encoded difference from repaired R2
  2.86102e-6; proposal oracle parity worst 6.18716e-5, within the existing RGB
  fixture envelope. This is not a newly certified host envelope.
- 253 finite stress inputs: zero nonfinite outputs.
- The full blue ramp still has a .02105095 maximum adjacent linear channel
  difference at offsets 572->573, where an LMS component crosses zero. This
  preexisting positive-L signed-cube-root sensitivity also exists in R2. The
  proposal removes the huge guard jump, not every Oklab gamut-edge steep slope.

## Existing real material, offline full-pixel comparison

The two previously used CC BY Tears of Steel EXRs were scanned in full, assuming
scene-linear Rec.709 as in the existing host evidence. Embedded primaries were
not newly certified. Sources/attribution: (CC) Blender Foundation |
mango.blender.org; https://ftp.lysator.liu.se/pub/xiph/media/tearsofsteel/tearsofsteel-footage-exr/README.txt .

Each frame has 8847360 pixels:

- Skin 05_3a_01105: 27757 source pixels contain negative RGB; 7827 nonblack pixels
  (0.08847%) hit the L guard. Proposal changes 6475 pixels by >1e-4 encoded;
  maximum guarded-region encoded difference .1049292.
- Highlight 06_1b_00245: 47385 source pixels contain negative RGB; 4474 nonblack
  pixels (0.05057%) hit the guard. Proposal changes 3554 pixels by >1e-4 encoded;
  maximum guarded-region difference .0935764.
- Positive-L model output is identical by construction; no new nonfinite output.
  Native positive-domain float differences are reported separately above.

Thus the issue is **not proven irrelevant to real material**, and the changed
pixels are not assumed invisible because their count is small. This is an
offline source-model impact comparison, not matched Resolve renders or user
visual acceptance. See real-material.json for exact source hashes and limits.

## Required next decision

Recommended: review the continuous signed-L proposal as a bounded product
revision, then test the exact approved artifact in Resolve before promoting it.
Alternatively retain R2 and explicitly accept its domain discontinuity as a
known limitation. The latter does not satisfy a claim that the reported blue
boundary is fixed. A larger Oklab replacement is a distinct design decision,
not something hidden in this repair.

GPU `_fmaf`/parser validation, matched real-material comparisons, runtime cost,
alpha/identity regression and user visual acceptance remain required. Native
CPU timings, when present, are only a microbenchmark and cannot establish 4K
Resolve performance. See STABILITY_HOST_HANDOFF.md.

## Final verification and CPU timing

Final focused suite: 21 tests passed on Linux GCC and Windows MSVC. Windows
log: evidence/stability-20261107/tests-final.log. No tests were skipped.

Windows CPU microbenchmark medians for 1,000,000 samples were baseline 198.2612
ms, R2 scalar repair 311.7235 ms (1.5723x), continuous proposal 404.7230 ms
(2.0414x), five alternating-order runs of 256 fixed blue-biased inputs. This
workload includes negative-L samples that the baseline bypasses. It is not a
representative Resolve workload or a GPU/4K acceptance result. Measure actual
GPU runtime before deciding that either new artifact is usable. See
evidence/stability-20261107/native-performance.json and tools/benchmark_native.py.

Installed SDK README SHA256: 9a227dfc276cea11be2b7ac3d3d080a77e0cd21f6b7d1b4cb09bf0d99bb12efe.
