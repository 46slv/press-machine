# DEV-12 R2 local implementation log

2026-11-05: accepted new R2 implementation delegation. This supersedes the older
legacy-density objective for this turn; no old checkout, branch or deployment is
modified. GUI ownership remains with parent.

- Fresh authorized Git heads: main `a926635f52411fcd15486790008d38169fcea623`,
  docs `75a9fbfbe0f8cfb328257f27dda3ec0eb8d3f936`, legacy
  `430aa1528c55abedfc6328cec6873432a374f27d`, historical feature/PR #1
  `41b2f57f650d8bfe48881d5cc3c59c77c071170e`.
- Fresh clone `press-machine-dev12-r2`; local branch
  `dev/dev12-r2-dwg-di-20261105`. Branch absent from live remote and local refs
  before creation. No PressMachine writer claim found in local writer registry;
  old checkout has only its clean A2 worktree. This log claims this new checkout
  and branch for this task, not the other lanes.
- Read checkout/ancestor instructions (no AGENTS.md found), shared coding Git
  instructions, live DEV-12, R4 and SAT-001..020. Read primary BM v1.1 and current
  W3C conversion data; inspected historical PR's oracle/harness as reference.
  Historical source selectors/Ratio and its old S scale are not adopted.
- Existing MSVC 2019 compiler found. No toolchain installation or auth change.
- Local runtime model identifier is not exposed in available execution metadata;
  `gpt-6.1-sol` cannot be independently confirmed. No model substitution or worker
  delegation was requested/performed here.

Implementation complete: four controls, signed-root Oklab, original-RGB fast
paths, independent double oracle, native compilation of actual DCTL. Host gates
remain NOT RUN; no Resolve/GUI/installation operation authorized in this turn.

2026-11-05 qualification checkpoint:

- 11 focused reference/source tests PASS; native 180,280 scalar samples,
  336 color/control cases, 253 finite stress inputs, 24 direct domain guards,
  8 conversion anchors and 2 nonfinite bypass payload cases pass.
- 43,324 scalar and 219 RGB exact identities. Two near-C-guard crossings are
  exposed in the report; maximum difference there 1.986e-12. No epsilon change.
- Measured worst RGB error 6.187159905e-5; frozen normalized envelope is the
  next binary boundary, 1.220703125e-4. Worst sample's near-zero LMS sensitivity
  is retained as an R6/R7 risk rather than hidden with a new curve/clamp.
- 53 patches, 8 float RGBA EXRs generated. Existing FFmpeg independently
  decoded 114,688 channel words exactly. Host compile/alpha/visual/performance
  remain NOT RUN. See PREBUILD_REPORT.md and docs/HOST_HANDOFF.md.
- Read-only preservation check confirms A2 f0b5241, partial v1.2.2 2d8acba,
  legacy 430aa15 and proposal 7e1870c unchanged; old checkout remains clean.
- Branch was exclusively created here; no external writer was observed.
  Preparing one local commit. No push/PR/merge/install or GUI mutation.
