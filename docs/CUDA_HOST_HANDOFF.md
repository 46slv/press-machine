# Exact CUDA candidate: next Resolve gate

Source branch: `dev/dev12-cuda-rounding-20261107` at its verified remote head.
Product file: `dctl/PressMachine_R2.dctl`.
SHA256: `97f008ae91789b2391e9742839b0afc24a7587993e22f108d42dfa7ebd894f1e`.
[Cause and measurements](CUDA_ROUNDING_REPORT.md).

Do not reuse the previous failing artifact (`ade36d...`) or carry its old alpha
pass forward as acceptance of this changed source.

1. Read live DEV-12 R2, latest user instructions and ownership records. Check
   current source writer, Resolve projects, unsaved changes and active renders.
   Claim one host lane. Preserve all existing user state. Do not overwrite,
   delete, relink or replace the previous numeric project or evidence.
2. Freshly inspect the released prior host folder
   `D:/Documents/Codex/PressMachine-Boundary-Host-20261107/`.
   It contains the exact binary32 input EXR, numeric manifest and failed readback.
   Owner release and idle state are historical and must be rechecked.
3. Use a NEW unique scratch folder/project/DCTL staging name. Hash the staged
   product against the exact hash above, including after any line-ending copy.
   Preserve/restore any installed file; do not promote it into the user's tools.
   Record Resolve version, explicit processing GPU, timeline and output settings.
4. Recreate the same float-RGBA numeric path: DWG/DaVinci Intermediate input and
   output, no CST, LUT, display bake, grading, scaling, cache or extra transforms.
   Render float EXR Bypass, C0, C75 at T25/Softness20 and repeat C75.
   Verify each sampled input word against the original manifest. Preserve alpha.
5. Read actual EXR float words, not screenshots. Use all 9894 manifest records
   and original independent double expectations, normalized RGB envelope 2^-13.
   Require zero nonfinite outputs/exceedances; no budget widening or masking.
   Check original regression and HDR plane2 index9624 explicitly.
6. Require full-frame alpha equality, C0/bypass exact word equality, selected
   identity pixels, and deterministic repeated C75. Save CSV/JSON, exact source,
   source hash, compiler/Resolve logs and project archive in the new folder.
   CUDA source includes raw RN intrinsics and cbrtf; a DCTL compilation failure
   is an unpassed gate, not permission to omit compensation or use another file.
7. Only after numeric/control/alpha PASS, continue the earlier
   [matched real-material and 4K plan](BOUNDARY_HOST_HANDOFF.md).
   CPU/standalone CUDA timing is not Resolve usability or visual acceptance.
   The contract L-guard discontinuity and signed-root cusp remain expected.
8. Restore original project/file state, save evidence, remove temporary staging
   only after verification, record host writer release and report exact PASS/FAIL,
   failures, hashes and unfinished gates.

No main merge, release, public visibility change or installation is authorized
by this handoff. A later integration step must use the user's current permission.
