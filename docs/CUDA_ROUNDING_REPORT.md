# CUDA rounding repair, 2026-11-07

Status: same-contract development candidate. Native and standalone CUDA gates
pass. This exact artifact has NOT passed Resolve, alpha, real-material, 4K or
user visual acceptance. Do not deploy or call it a finished usable version.

Current branch: `dev/dev12-cuda-rounding-20261107`.
Current source SHA256:
`97f008ae91789b2391e9742839b0afc24a7587993e22f108d42dfa7ebd894f1e`.
Base checkpoint: `a567e1a41d5913be0beeb30bc2651d804ce647e9`.

## Actual host failure and cause isolation

The preceding source (`ade36d9359644fa0a47a291cd9ca16c3025f2253aeeaa6135905d8d5c6d2b331`)
passed CPU qualification but FAILED Resolve 21.1.0.14 CUDA on RTX 3070 Ti:
947/9894 numeric labels exceeded the unchanged 2^-13 normalized RGB envelope;
maximum normalized error was 1.0902709382. Bypass input was bit-verified, C0
matched bypass, alpha matched exactly, and repeat C75 was byte-identical.
Those control results belong to the OLD artifact, not the new candidate.

Local raw evidence:
`D:/Documents/Codex/PressMachine-Boundary-Host-20261107/HOST_RESULT.md`,
`numeric-errors.csv`, `numeric_manifest.json`, and float RGBA EXRs.
The compact synthetic numeric fixture in Git retains exact inputs, independent
double expectations and old-host sampled outputs without requiring footage.

Using the same compute GPU and already installed signed Resolve NVRTC 12.8:
- Old actual source, FMA contraction enabled: 933 envelope failures.
- Same source, contraction disabled: zero failures.
- Fast-math: 947 failures, maximum 1.0902957361, matching the host failure pattern.
- Fast-math with contraction disabled: one failure remained.

This ablation identifies compiler contraction and approximate arithmetic as
causes of destroyed compensation. It does NOT establish Resolve's exact
compiler options or bit-for-bit equivalence of the standalone wrapper.

## Repair

- Explicit CUDA round-to-nearest add/subtract/multiply/divide/FMA intrinsics
  preserve each required rounding boundary in compensated float-pair arithmetic.
- The existing near-cancelling LMS routing region, 2^-8 of largest LMS magnitude,
  now retains pairs through signed roots, Lab, chroma, C/L, the SAME scalar curve,
  inverse roots/cubes, and published matrices. Premature float Lab/S rounding
  otherwise amplifies error while HDR outputs subtract large terms.
- Two Newton residual corrections refine the signed cube-root seed; a square-root
  correction refines chroma. Exact zero exits avoid 0/0. An exact 1/8 reduction
  followed by x2 prevents cube residual overflow near float maximum.
- CUDA's T=0/C=100 finite-positive-S endpoint is explicitly zero using integer
  classification. Fast-math comparisons otherwise treated tiny positive
  subnormals as zero and returned them unchanged, causing four sampled decreases.
  Negative/zero/nonfinite scalar handling and the earlier C0 return are preserved.
- Non-CUDA uses portable volatile rounding boundaries under strict floating-point
  compilation. No cross-backend fast-math or subnormal guarantee is claimed.
- Constants are independently copied as decimal strings from published tables,
  not imported from the oracle. The oracle, frozen budgets and unapproved
  continuous-domain proposal are byte-unchanged.

No clamp, smoothing, gamut mapping, weighting, domain revision or artistic
change was added.

## Final measurements

`evidence/cuda-rounding-20261107/final.json`:
four optimizer modes x 9894 original host numeric vectors, zero nonfinite outputs
and zero envelope failures. Worst across modes: 3.765739317e-7 normalized RGB.

`expanded.json`:
- Four modes x 14826 extra HDR/cancellation and adjacent-ULP vectors, zero failures.
  Worst normalized RGB error: 2.356442441e-7.
- Four modes x 677742 scalar cases (421486 expanded + 256256 high-tail), zero
  envelope failures, decreases, boosts, negatives, nonfinite results or C0
  identity failures. Worst normalized scalar error: 5.958137293e-8, below 2^-23.
- Exact subnormal-threshold identity regression: 16 cases per mode, zero word failures.
- C0 and bypass: 24722 RGB vectors each, including signed zeros and nonfinite
  payloads, zero word mismatches. This is standalone RGB, not a host alpha test.

`native-tests.log`: 34 MSVC strict-mode tests PASS, no skips.
`native-qualification.json`: original frozen corpus, boundary 8196, all-plane
1514, and routing seams 130 pass without revised budgets.
All standalone contexts, modules and device allocations are released in finally
blocks. No Resolve project, installed DCTL, GPU preference or runtime was changed.

A test-development error initially passed NumPy float32 values into the double
oracle; that invalid pixel report was discarded from qualification and retained
only in ignored local build scratch. Final expected RGB computations explicitly
convert inputs to Python floats. A regression test verifies saved host expectations.

## Reproduce

CPU (standard library and an available supported native compiler):
```powershell
python -m unittest discover -s tests -v
python tools/qualify_boundary.py --output build/native-qualification-resume.json
```

CUDA is an explicit Windows/RTX-3070-Ti qualification, using installed Resolve
NVRTC and existing NumPy. Freshly check host ownership, idle target GPU and
runtime provenance before executing. No toolkit installation is needed.
```powershell
python tools/cuda_probe.py --output build/cuda-host-vectors-resume.json
python tools/qualify_cuda_rounding.py --output build/cuda-expanded-resume.json
```
Use `--source` on cuda_probe with the old Git source to reproduce the ablation.
Use `--host` only when the original host folder is available; the default uses
the portable synthetic fixture. NVRTC wrapper results are not Resolve qualification.

## Remaining gates and model boundaries

Follow [CUDA_HOST_HANDOFF.md](CUDA_HOST_HANDOFF.md) for a fresh host gate.
Actual Resolve compilation and numeric readback may differ from NVRTC.
New-source GCC, non-CUDA GPUs, 4K performance and actual-material visual
acceptance remain unmeasured. No GPU performance claim is inferred.

The prescribed L<=1e-6 identity jump and the exact signed-cube-root continuous
cusp remain. Removing either requires an explicit product/model decision.
The isolated continuous-domain proposal remains unapproved and unchanged.
