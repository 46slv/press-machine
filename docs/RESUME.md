# PressMachine resume checkpoint

## Start here

This is a development checkpoint, not an accepted usable version or a release.
The canonical product contract is the approved
[DEV-12 Revision 2 brief](https://app.notion.com/p/3e4fd279a6f381cf85f1e121b69f86f7).

Canonical repository: https://github.com/46slv/press-machine .
The repository is public. Saving these development branches does not merge them
into main or change repository visibility.

## Preserved versions

All local working copies were clean at this handoff.

| Lane | Branch | Implementation checkpoint | Local folder under task-4 |
| --- | --- | --- | --- |
| Earlier A2 experiment | prototype/press-machine-a2-20261020 | f0b5241 | press-machine |
| Earlier partial legacy repair | fix/press-machine-neutral-density-task4-20261020 | 2d8acba | same earlier repository |
| Earlier curve design | design/press-machine-continuous-neutral-20261020 | 7e1870c | same earlier repository |
| R2 original/conditioned baseline | dev/dev12-r2-dwg-di-20261105 | 37e0c2e | press-machine-dev12-r2 |
| R2 scalar stability + isolated domain proposal | dev/dev12-r2-stability-20261107 | 7e48d7b | press-machine-dev12-stability-20261107 |
| Current R2 LMS precision repair | dev/dev12-boundary-diagnosis-20261107 | 204d601 source, edbe67d evidence normalization; later documentation commit contains this file | press-machine-dev12-boundary-20261107 |

The common parent directory is
`C:/Users/shiro/Documents/Codex/2026-10-20/task-4/`.
Do not overwrite, reset or remove the earlier lanes merely to resume this one.
Remote branch heads, rather than an old local path, are the portable entry point.

Current product source: `dctl/PressMachine_R2.dctl`.
SHA256: `ade36d9359644fa0a47a291cd9ca16c3025f2253aeeaa6135905d8d5c6d2b331`.

## What is saved

- Source, independent reference, native harness, deterministic fixtures and tests.
- Current explanation: [BOUNDARY_REPAIR_REPORT.md](BOUNDARY_REPAIR_REPORT.md).
- Exact-artifact host steps: [BOUNDARY_HOST_HANDOFF.md](BOUNDARY_HOST_HANDOFF.md).
- Qualification, preservation record, CPU measurement and 30-test log:
  `evidence/boundary-20261107/`.
- Historical scalar/domain evidence remains in the stability branch and
  `docs/STABILITY_REPORT.md`.
- Existing target-host scratch/evidence is outside Git at
  `D:/Documents/Codex/PressMachine-AR3-20261107/`.
  It must be inspected afresh before reuse. Actual footage and host project
  state are not reconstructed by cloning this source repository.

The current candidate's 30 focused MSVC tests passed without skipped tests.
The frozen numerical budgets were not widened. New-source GCC and Resolve/GPU,
alpha, 4K usability and user visual gates have not been executed.

## Remaining issues, do not conflate them

1. The extra float precision defect around LMS zero is repaired. On 8196
   binary32 input samples, maximum normalized error fell from .00436265 to
   3.17334e-7 and existing-envelope exceedances fell from 4 to 0.
2. The original R2 L<=1e-6 identity guard still causes the large blue boundary.
   Removing that behavior requires a product-domain revision decision.
3. The separate .0210512 adjacent blue difference is also present in the
   independent double reference. It is a continuous signed-root cusp, not
   proof of a second finite discontinuity. Smoothing it changes the model
   or its invariants.
4. `prototypes/PressMachine_ContinuousDomain.dctl` is an unchanged,
   unapproved domain proposal. It does not contain the new precision repair.
   Do not silently promote it or treat it as the current product.

CPU microbenchmark ratio was 1.1980 versus the preceding R2 candidate on its
fixed blue-ramp workload. This does not establish GPU or 4K performance.

## Resume procedure

1. Read this file, the live DEV-12 brief, and the two BOUNDARY documents.
   Inspect branch/HEAD, uncommitted changes and current ownership before editing.
   Source writer was released; no Resolve/GUI writer is claimed by this checkpoint.
2. Check the latest instruction and decide the unresolved product-domain issue
   before claiming the blue boundary is fixed. Keep experimental revisions
   separate from R2.
3. If source changes, repeat the native checks with unique output paths:

```powershell
python -m unittest discover -s tests -v
python tools/qualify_boundary.py --output build/qualification-resume.json
python tools/benchmark_boundary.py --output build/performance-resume.json
git diff --check
```

4. For the exact current hash, follow BOUNDARY_HOST_HANDOFF.md after freshly
   checking host ownership, save state, active renders and scratch project.
   Verify GPU arithmetic, changed-artifact identity/alpha and numeric fixtures.
5. Continue matched real-material/4K checks and obtain the user's visual
   acceptance. Then separately perform authorized canonical integration and
   merged-artifact installation/smoke. Do not call the case complete before
   those gates are met.

No protected-main merge, release, force push, history rewrite or repository
visibility change is part of this checkpoint.
