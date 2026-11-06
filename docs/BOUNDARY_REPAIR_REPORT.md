# R2 LMS precision repair and remaining model boundary

## Result

The R2 numerical implementation is repaired locally. This is **not** a usable
version, Resolve/GPU pass, visual acceptance or product-domain revision.

Base: `7e48d7b1ac55eac23739d0a1f620b35779aa7a40`.
Current DCTL SHA256: `ade36d9359644fa0a47a291cd9ca16c3025f2253aeeaa6135905d8d5c6d2b331`.
Owned branch: `dev/dev12-boundary-diagnosis-20261107`.
The prior source worktrees and continuous-domain proposal are preserved.

## Three separate causes

1. **R2 L-domain jump:** The approved original-RGB guard at L<=1e-6 produces
   the previously recorded .7215 blue jump around offsets 689->690. This
   guard and its behavior are unchanged. Removing that jump still requires a
   product-domain decision. The isolated absolute-L proposal is unapproved.
2. **Exact-model LMS cusp:** At blue ramp offset 572.61336, LMS component 0
   crosses zero while Oklab L is about .24624. The signed cube root is
   continuous but has an unbounded derivative. Active chroma scaling breaks
   the forward/inverse cancellation of the identity mapping.
   The independent double oracle reproduces the .0210512 adjacent blue drop
   at 572->573. On successively four-times-finer intervals the symmetric
   difference tends to zero with ratio .62996, matching 4^(-1/3). This is a
   continuous cusp, not evidence of a second finite discontinuity.
3. **Additional float precision defect:** Inputs immediately around the LMS
   zero amplify ordinary decode/matrix rounding. On 8196 encoded-binary32
   inputs, native/oracle normalized error reached .00436265 and 4 samples
   exceeded the existing empirical RGB envelope 2^-13. Both sides used the
   same encoded inputs, so this is not source-quantization mismatch.

The repair addresses item 3 only. Items 1 and 2 must not be advertised as fixed.

## Implementation

When any fast LMS component is at most 2^-8 of the largest component, recompute
the **same** DI decoding and two published matrix products in compensated
float pairs. Round the recovered LMS back to binary32, then use the original
signed root, Oklab model, scalar law and reconstruction.

The log decode uses a degree-16 Taylor polynomial for 2^r on [0,1], integer
power-of-two scaling, and split constants from the original decimal references.
The analytic Taylor truncation is below 1.4e-17 before pair rounding. Exponents
above 127 retain the existing fast decode/range handling.

There is no new creative epsilon, blend, gamut map, lightness weighting,
clamp, control, guard or saturation definition. This approximates the same
reference expression more accurately; it is intentionally not bitwise
equivalent on affected compressed pixels. The independent oracle and frozen
budget are unchanged. `generate_precision_candidate.py` reproduces the
current DCTL from the pinned baseline and decimal constants.

## Executed verification

Windows 11 / Python 3.12.10 / existing MSVC 19.29.30137, C++17 O2 strict FP:

- 30 focused tests PASS, no skipped tests.
- Original 180280 scalar, 336 RGB, 253 finite stress, 24 direct-domain,
  8 conversion and 2 nonfinite-bypass cases pass unchanged budgets.
- Original RGB maximum normalized error: 6.18716e-5 -> 8.93232e-7.
  The same two historical C-guard crossings remain explicitly reported.
- Expanded 421486 scalar and 256256 high-tail samples still pass the existing
  scalar 2^-23 envelope with no sampled local decrease, boost or nonfinite.
- LMS-zero neighborhood 8196 samples: .00436265 -> 3.17334e-7 maximum
  normalized error; envelope exceedances 4 -> 0.
- All three LMS cancellation planes: 1514 positive-L samples; maximum
  normalized error 4.67194e-5, no envelope exceedance or new nonfinite.
- Precision routing seams: 130 samples; maximum encoded error 3.76574e-7,
  no envelope exceedance.
- Direct compensated decode tests cover seeded values, DI branch neighbors,
  exponent boundaries and the exponent-127 fallback transition.
- Independent source review found no material source-level defect and
  confirmed that the product model/guard contract is unchanged.
- `git diff --check` passes.

Commands:

```powershell
python -m unittest discover -s tests -v
python tools/qualify_boundary.py --output build/qualification-unique.json
python tools/benchmark_boundary.py --output build/performance-unique.json
git diff --check
```

Evidence is in `evidence/boundary-20261107/`. The historical frozen envelope is
an empirical fixture envelope, not a universal GPU error bound. This repair's
cross-platform GCC requalification was not performed; do not reuse the older
candidate's GCC result as evidence for this source.

## Cost and remaining gates

The fixed 256-point blue-ramp CPU microbenchmark (one million samples, five
alternating-order runs) measured medians 276.9145 ms baseline and 331.7505 ms
repair, ratio 1.1980. This is not GPU time, 4K usability or a representative
footage benchmark.

The new source has **not** been loaded, installed or rendered in Resolve.
Its float-pair ordering, true fused FMA behavior, integer scaling and GPU
compiler need exact-artifact qualification. Identity, alpha, extended range,
real-material matched comparison, runtime cost and user visual judgment remain
open. The old host comparisons describe other hashes.

A smoother positive-domain response than the reference cusp requires changing
the model, f(S), or L/hue invariants. Under positive L/C, the existing contract
uniquely fixes a_out and b_out and leaves no independent smoothing degree of
freedom. Do not hide such a revision inside this precision repair.

No push, PR, merge, production deployment, Resolve operation, Notion-contract
change or external publication was performed.
