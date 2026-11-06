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

2026-11-05 source correction after released R6:

- Parent authorized only source/oracle/native work in this same owned checkout
  and branch. Clean d3964ac starting state, single worktree, no index lock or
  competing writer observed. No GUI, Resolve console/restart, DCTL staging or
  install used. All 46 external R6 evidence files were hashed before editing.
- Reproduced the old native S500/T.8/C99.7/P59.5 regression before editing:
  2.2976105213165283 vs oracle2.29761524626017. Exact source/executable receipt
  retained. Read official installed SDK README/Gain as provenance.
- Changed only DCTL entry physical layout and algebraic high-tail q evaluation.
  Knee polynomial, four controls, oracle and protected pixel behavior unchanged.
- 13 tests PASS (original11 + literal SDK layout + native case regression).
  Conditioned native2.2976152896881104, absolute error4.342794035494535e-8;
  justified case-only gamma4 bound5.477947476871242e-7. No global budget change.
- New tools/scalar_measure.py checks the original corpus with unchanged frozen
  budgets, then separately measures seeded fractional neighbors and high tails.
  Reports write to evidence/repair-20261105; historical reports remain intact.
- Original 180,280 scalar and 336 RGB cases, 253 finite stress, 24 guards,
  8 anchors, 2 bypass payload cases PASS; exact identities/guard crossings and
  worst scalar/RGB errors unchanged. Existing MSVC19.29.30137 strict FP.
- Expanded 421,486 points/12,080 states: maximum normalized1.780754835689492e-7,
  943 local decreases, max drop3.0517578125e-5; no boosts/negative/nonfinite/C0
  identity failures. High tail256,256 points: max normalized2.0360922633961318e-7,
  no nonfinite/boost/negative/C0 failures. Matches independent parent GCC data.
- Expanded maxima exceed original corpus2^-23. No expanded budget adopted;
  strict float-output monotonicity remains false on sampled adjacent pairs.
  Analytic monotonicity, numeric precision and bit-monotonicity kept distinct.
- New native parser validation/Color Page GPU/alpha/4K/visual gates remain
  NOT RUN. Canonical layout fixes only a plausible parser cause until native
  evidence exists. Reviewing diff and preservation before one normal local commit.

2026-11-07 isolated scalar/domain investigation:

- Fresh original branch 37e0c2e was clean. Parent confirmed prior host/source writer release; this task claimed only the new worktree press-machine-dev12-stability-20261107 and branch dev/dev12-r2-stability-20261107. No Resolve/GUI/installation operation was performed.
- Reproduced the exact previous synthetic blue boundary in both independent CPU oracle and actual DCTL native execution. The mandated L guard is the cause; an epsilon-only repair cannot remove the zero-L discontinuity.
- R2-compatible compensated scalar arithmetic resolves all 943 sampled local decreases and keeps the unchanged frozen budgets. GCC/MSVC agree; 21 final focused tests pass.
- Separate prototypes/ continuous signed-L proposal reduces the recorded blue jump .72150 to .00084226. It deliberately changes the L-domain exception policy and is not the approved product or a deployed artifact. Existing positive-L LMS-zero sensitivity remains.
- Full offline source-model comparison on the existing skin/highlight EXRs finds L-guard pixels .08847%/.05057%, with maximum changed encoded values .10493/.09358. Positive-L model outputs agree. Colour interpretation remains documented assumption. No new visual acceptance.
- Windows CPU microbenchmark is slower (R2 scalar 1.57x, domain proposal 2.04x baseline); actual GPU cost and usability remain untested. Reports, exact hashes, source assumptions and bounded host handoff are saved.
- Current Notion R2, reference/oracle.py, frozen parity budget, old source checkout and installed DCTLs remain unchanged. Preparing one local candidate commit only; no push/PR/merge/release. Source writer will be released after clean final readback.

Final source/evidence commit dfd4ec7 completed. Follow-up metadata normalization makes evidence hashes match canonical LF repository bytes; no DCTL/source logic changed after the 21-test pass. The original R2 checkout remains clean at 37e0c2e. Source writer is RELEASED; a later owner must freshly bind the branch/host and respect the pending product-domain decision. No push, PR, merge, install or Resolve operation occurred.

2026-11-07 remaining-boundary diagnosis:

- Fresh source candidate 7e48d7b1 was clean and recorded source writer RELEASED. This task claims only the new independent worktree press-machine-dev12-boundary-20261107 and branch dev/dev12-boundary-diagnosis-20261107, based on that exact commit.
- Scope: independently separate the remaining LMS-zero steep slope from GPU/native precision, and identify the exact contract boundary. Product DCTL, oracle, current Notion R2, installed artifacts and all host state remain unchanged. No push/publication is in scope.
- Existing host CHECKPOINT records the earlier 21.1.0.14 comparison and host release. No new Resolve operation is performed.

- Found an additional contract-compatible arithmetic defect: 8196 binary32 encoded inputs around the LMS zero had maximum native/oracle normalized error .00436265, four beyond the unchanged empirical RGB envelope. A compensated DI/matrix fallback reduces this to 3.17334e-7 with zero exceedances. The independent oracle, scalar law, original L/C/S guards and unapproved continuous proposal are unchanged.
- The remaining .0210512 adjacent blue drop is also present in the independent double model. Shrinking-interval convergence matches the signed-cube-root continuous cusp; it is not a second finite jump. The original L-guard discontinuity is still an unresolved product-domain decision.
- Final MSVC strict-FP suite: 30 tests PASS, no skips. Original frozen corpus and expanded scalar suites pass unchanged budgets; all-three-plane 1514-case and 130-point precision-routing seam checks pass. Exponent-127 fallback is explicitly tested. Exact source, qualification and handoff are in docs/BOUNDARY_REPAIR_REPORT.md, docs/BOUNDARY_HOST_HANDOFF.md and evidence/boundary-20261107/.
- Existing R2 and stability worktrees are clean at 37e0c2e and 7e48d7b1. Reference/oracle, frozen budget and continuous proposal are byte-preserved. CPU blue-ramp median ratio is 1.1980; no GPU/4K result is inferred. New-source GCC and all new Resolve/alpha/visual gates are NOT RUN. No push, PR, merge, installation, host operation or Notion-contract change.
- Preparing one normal local checkpoint commit after diff review. Source writer is RELEASED on the clean final readback; later owners must freshly claim this branch/host and respect the pending product decision.

Resume/preservation checkpoint: Added docs/RESUME.md as the single portable entry point for the original, A2, stability and precision lanes, evidence and unfinished gates. Fresh readback found every worktree clean and verified source hash/evidence. Existing origin is public; development-branch publication was explicitly authorized after disclosure. Main, repository visibility, installed artifacts and Resolve remain unchanged. No product source changed in this documentation checkpoint.
