# Next gate: R6 Resolve qualification — NOT EXECUTED

This task performed no GUI, Resolve, project, installation or deployment action.
Parent owns GUI coordination. Do not reuse A2's tiny Fusion experiment as R2
evidence. Before testing, the next owner must recheck current Resolve state,
scratch-project ownership and the unresolved historical restoration checkpoint.
Do not close/restart Resolve or switch projects based on this handoff alone.

## Candidate and fixtures

- Branch `dev/dev12-r2-dwg-di-20261105`; commit is the local commit containing
  this file. Resolve the full SHA with `git rev-parse HEAD` and record it before
  staging the candidate. Final task delivery also records its full SHA.
- DCTL `dctl/PressMachine_R2.dctl`, SHA256
  `35442c75a7b31c6da0bfe94dfa8cbb6b3ab13737752bb81a36afa28ed2b671b8`.
- `fixtures/host/manifest.json`: dimensions, patch-center coordinates, exact
  encoded float32 inputs, alpha, six control states and double oracle outputs.
- Eight uncompressed FLOAT RGBA EXRs, 64x56, 53 authored 8x8 patches. Black
  padding fills the last row. `patches.csv` lists expected S and output per state.
- `input_dwg_di.exr`: actual DWG/DI node-input fixture, for a direct numerical
  node-output comparison under topology B. Disable automatic source conversion.
- `input_linear_dwg.exr`: same colors decoded to linear DWG, for topology A.
  CST In: input DWG / Linear; output DWG / DaVinci Intermediate; tone mapping
  None, gamut mapping None. Expected EXRs are SatComp-node DWG/DI outputs,
  before CST Out. No camera space should be assigned to these authored fixtures.
- Expected EXRs: bypass, zero compression, moderate (T25/C50/P20), strong
  (T25/C100/P100), hard_zero (T0/C75/P0), untouched (T200/C75/P20).
  The last state is untouched only for S<=160; high-S patches can still compress.
- Authored alpha cycles 0/.25/.5/1, including colors with nonzero RGB at alpha0.
  File readback proves serialization, not Resolve's premultiplication/alpha path.
  Inspect the target buffer convention before drawing alpha/RGB conclusions.

## Planned target checks

1. Record live Resolve 21.x build, OS/GPU/backend, exact candidate commit and
   DCTL hash, actual clip/project management and CST settings. Use an owned
   scratch fixture with a documented recovery path under the GUI owner's control.
2. Stage candidate only when that later operation is authorized. Load/compile
   in Color Page and check four controls/default identity. Native compilation
   does not prove DCTL host macro parsing or GPU compilation.
3. Compare DCTL node float buffers against the same float32 input fixture and
   manifest oracle. Exercise the six control states and direct synthetic numeric
   patches. Exact bypass/Compression0/untouched comparisons use the same
   surrounding CST chain and must be bit-preserving at the DCTL boundary.
   If only post-CST/export buffers are available, first characterize that path;
   never assume the surrounding CST or export is an identity transform.
4. Apply the frozen prebuild-derived **candidate** envelope in
   `evidence/parity_budget.json` at the DCTL DWG/DI node boundary:
   RGB error <= `0.0001220703125 * max(1, max(abs(oracle RGB)))` per pixel.
   Scalar normalized limit is `1.1920928955078125e-7`. This is empirical for this
   corpus, not a universal GPU bound. If host error exceeds it, classify the
   compiler/math/buffer/CST/export cause before repair; do not silently widen it.
   Guard-boundary cases listed in `prebuild.json` remain explicitly identified.
5. Verify finite negative and >1 values survive the intended DCTL boundary,
   finite output, negative-LMS behavior, invalid-domain identity and actual
   alpha preservation. Direct DCTL buffers are needed to separate output
   rendering/gamut handling from SatComp behavior.
6. Measure the same representative 4K timeline with/without SatComp, then set
   and record the performance comparison criterion. The tiny EXR atlas is a
   numeric fixture, not a performance benchmark.
7. Under the same output/display path inspect skin, neon/LED, saturated red/blue,
   dark saturated, gamut-edge and HDR material. User visual acceptance remains
   required. Visible hue/lightness shifts, threshold banding or near-black
   artifacts fail acceptance even if prebuild arithmetic passes.

No target Resolve build, installation, host numeric/alpha/extended-range result,
4K performance or user visual PASS is asserted. R8 integration/publication and
R9 completion remain later gates. Publication as a reviewable branch/PR may be
useful after review, but was not performed or requested in this task.
