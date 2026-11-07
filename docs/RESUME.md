# PressMachine resume checkpoint

Development checkpoint, not an accepted usable version or release.
Canonical contract: [DEV-12 Revision 2](https://app.notion.com/p/3e4fd279a6f381cf85f1e121b69f86f7).
Repository: https://github.com/46slv/press-machine (public, publication approved).
No main merge, visibility change, release, force push or history rewrite.

## Current lane

Resume branch `dev/dev12-cuda-rounding-20261107`, not the older CPU-only repair.
Product source: `dctl/PressMachine_R2.dctl`.
SHA256: `97f008ae91789b2391e9742839b0afc24a7587993e22f108d42dfa7ebd894f1e`.
Use the verified remote head and record `git rev-parse HEAD` before changing it.

- [Cause, exact changes and measurements](CUDA_ROUNDING_REPORT.md).
- [Next exact-artifact Resolve gate](CUDA_HOST_HANDOFF.md).
- Portable synthetic host fixtures, GPU ablations, final qualification and tests:
  `evidence/cuda-rounding-20261107/`.
- Source lane is released after final clean verification. Host/GUI ownership is
  NOT granted by this file: freshly check current ownership, projects and renders.

The preceding `ade36d...` source passed CPU tests but FAILED actual Resolve CUDA:
947/9894 numeric labels, maximum normalized error 1.0902709382.
Its Bypass/C0/alpha passes are historical and do not qualify the changed artifact.

The new source fixes FMA-contraction/approximate-arithmetic damage to compensated
float pairs and retains residuals through the near-cancelling color path.
Four same-GPU optimizer modes pass 9894 original numeric vectors and 14826
extra HDR/adjacent vectors. Each mode passes 677742 scalar cases and 16 exact
subnormal-threshold identity checks. Standalone C0/bypass have no RGB word
mismatches. The native strict-mode suite passes 34 tests without skips.
Frozen budgets, independent oracle and the unapproved domain proposal are unchanged.

**Still pending:** exact-source Resolve compile/numeric/control/alpha gate,
matched real material, 4K performance, user visual acceptance and any later
authorized integration/installation. New-source GCC/non-CUDA GPU results are
not available. Standalone NVRTC is not Resolve acceptance.

## Preserved earlier lanes

All older working copies were left clean. Do not reset, overwrite or remove them.

| Lane | Branch | Preserved checkpoint | Folder under task-4 |
| --- | --- | --- | --- |
| A2 experiment | prototype/press-machine-a2-20261020 | f0b5241 | press-machine |
| Partial legacy repair | fix/press-machine-neutral-density-task4-20261020 | 2d8acba | same earlier repository |
| Earlier curve design | design/press-machine-continuous-neutral-20261020 | 7e1870c | same earlier repository |
| R2 original | dev/dev12-r2-dwg-di-20261105 | 37e0c2e | press-machine-dev12-r2 |
| Scalar stability / domain proposal | dev/dev12-r2-stability-20261107 | 7e48d7b | press-machine-dev12-stability-20261107 |
| CPU precision repair, later failed CUDA host | dev/dev12-boundary-diagnosis-20261107 | a567e1a; source204d601, evidence edbe67d | press-machine-dev12-boundary-20261107 |
| Current CUDA repair | dev/dev12-cuda-rounding-20261107 | this branch's verified remote head | press-machine-dev12-cuda-rounding-20261107 |

Common local parent: `C:/Users/shiro/Documents/Codex/2026-10-20/task-4/`.
All earlier branch refs were backed up to the same repository. Remote refs are
the portable entry point; footage, Resolve projects and host state are not
reconstructed merely by cloning source.

Prior raw host evidence:
`D:/Documents/Codex/PressMachine-Boundary-Host-20261107/`.
Earlier material scratch:
`D:/Documents/Codex/PressMachine-AR3-20261107/`.
Inspect current state before reuse and create a fresh output folder/project.

## Remaining model boundaries

1. The prescribed original L<=1e-6 identity guard causes the large blue jump.
   Removing it requires a product-domain revision decision.
2. The separate .0210512 adjacent blue difference is also present in the
   independent double model. It is a continuous signed-cube-root cusp.
   Smoothing it changes the model/invariants.
3. `prototypes/PressMachine_ContinuousDomain.dctl` is an unchanged, unapproved
   proposal. Never silently promote it into R2.

## Resume procedure

1. Read live contract, latest instructions, this file and CUDA reports. Inspect
   current writer, branch, HEAD and uncommitted work. Claim only one source lane.
2. For source changes, rerun native tests and qualification using unique paths:
```powershell
python -m unittest discover -s tests -v
python tools/qualify_boundary.py --output build/native-resume.json
git diff --check
```
3. If the exact authorized GPU/runtime is idle, repeat the explicit CUDA gates
   in CUDA_ROUNDING_REPORT.md. Preserve source/evidence hashes.
4. Follow CUDA_HOST_HANDOFF.md for a fresh Resolve gate. Never reuse old
   artifact passes, widen budgets, mask failing pixels or omit compile errors.
5. Only after host PASS continue material/4K and user acceptance. Integration,
   installed-artifact smoke and completion remain separate later gates.
