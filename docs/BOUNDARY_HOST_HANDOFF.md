# Exact-candidate handoff after the LMS precision repair

## Source and scope

- Branch: `dev/dev12-boundary-diagnosis-20261107`.
- Worktree: `C:/Users/shiro/Documents/Codex/2026-10-20/task-4/press-machine-dev12-boundary-20261107`.
- Candidate: `dctl/PressMachine_R2.dctl`, SHA256
  `ade36d9359644fa0a47a291cd9ca16c3025f2253aeeaa6135905d8d5c6d2b331`.
- Starting commit: `7e48d7b1ac55eac23739d0a1f620b35779aa7a40`.
  Use the commit containing this handoff as the new source checkpoint.
- Product contract remains current Notion Revision 2.
- `prototypes/PressMachine_ContinuousDomain.dctl` is unchanged and unapproved.
  It does not contain this new precision repair. Do not conflate artifacts.

Read BOUNDARY_REPAIR_REPORT.md and the machine-readable qualification report.
30 focused MSVC tests pass. No new host or user visual gate was executed.

## Next bounded checks

Freshly bind the exact host, project/save/render state and single writer.
Preserve existing projects and renders. The earlier host CHECKPOINT records
release, but do not assume current ownership from that historical entry.

1. Stage only a uniquely named, hash-verified copy of this exact R2 candidate.
   Confirm parser/load and real GPU execution, especially float2, _fmaf,
   _floorf, _fmaxf and compensated evaluation ordering.
2. Reproduce the numeric failure fixture from qualification.json:
   encoded input (.3940376341342926,.3940376341342926,.6125847101211548),
   T25/C75/P20. The new native output must be checked against the oracle
   rather than the older host artifact. Use the existing frozen RGB envelope
   without silently widening it.
3. Compare the same synthetic chart. At x2620->2621 / offsets572->573, the
   expected exact-model blue difference remains about -.0210512.
   Near offset572.61336, numerical noise should be reduced.
   The R2 L-guard jump at x2737->2738 / offsets689->690 remains expected.
   Neither should be marked visually accepted from numeric parity alone.
4. Target the 2^-8 routing seam and three LMS-zero planes with the supplied
   diagnostic vectors. Recheck changed-artifact C0/Bypass and untouched
   identity, finite negative/>1, alpha and representative 4K performance.
5. Use matched existing real-material stills before any broader acquisition.
   Retain prior color-metadata limitations. Judge dark/noise and gamut-edge
   regions as well as whole-frame appearance.
6. Save/export only the owned scratch, verify no active render before closing,
   remove only exact-hash task staging and release the writer.

## Decision boundary

A claim that the visible blue boundary is fixed still needs a product decision:
the original positive-L identity policy and the exact-model signed-root cusp
are separate. Do not adopt the absolute-L proposal or a smooth-metric change
without an explicit revision decision. User visual acceptance, canonical main
integration and merged-artifact installation/smoke remain incomplete.
