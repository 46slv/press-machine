# Continuous neutral proposal task log

## 2026-10-20 — scope and provenance

- Parent assessed `2d8acba3264de6f0c7d5cae4b67b0d6600804a77` as a partial
  v1.2.2 maintenance candidate. It removes phantom Sat Density below the old
  guard but leaves the chroma floor and a visible luma boundary step.
- Requested model: `gpt-6.1-sol`; actual runtime ID **UNVERIFIED**. No model
  selection or substitution was claimed. No fan-out or other agent queries.
- Existing isolated checkout was clean at that exact commit. One worktree was
  listed. New local ref `design/press-machine-continuous-neutral-20261020` was
  absent before creation, and this task is its sole observed writer. The
  previous candidate branch remains at `2d8acba`.
- Re-read relevant source and specification excerpts plus shared debugging/Git
  owners. No repository AGENTS.md found. All pre-existing versions and docs
  remain untouched.

## Derivation and finite decision

- Derived `L(0)=T*H((k-T)/(2k))`, positive exactly when `Ratio>1` and
  `0<T=Threshold^3<k=max(Knee,1e-6)`; positive Makeup transmits the floor.
- Compared affine and quadratic removals of the intercept, a no-expansion
  restriction, and a conventional knee with its lower edge kept nonnegative.
- Recommendation A2 subtracts `T*h0*(1-x/T)^2` only on the affected lower
  interval. It preserves the legacy Threshold value/left derivative and all
  raw curve values outside that interval, while retaining some creative lift.
- Derived an equivalent bounded gain and a continuous reconstruction/Density
  path. This must replace the old hard discard policy if full boundary
  continuity is wanted; it is not a one-point zero mask.
- Multiple different retained-lift behaviors satisfy the requested invariants.
  Existing docs separate newer compression-only behavior from legacy and do
  not select one. Therefore no experimental DCTL or new release version was
  created. The remaining issue is a creative curve choice, not an execution
  or safety/approval denial.

## Focused evidence

- Command: `python -B "Press Machine/legacy/neutral-continuity-proposal/probe_proposals.py"`
- Final result: **8 focused arithmetic groups passed, exit 0**. Complete
  numerical output and normalized source fingerprints are in PROBE_RESULTS.txt.
- The baseline executes scalar statements from preserved legacy source via
  the existing harness; no existing unittest suite or unrelated matrix ran.
- At default defect settings, A2's mathematical path gives Y
  `.179999460700` / `.179999460699` immediately across the old threshold,
  compared with v1.2.2's `.18` / `.177866640117`.
- The first probe run had 7 groups. A Threshold-slope comparison was then
  added because that distinguishes A1 from A2; the final 8-group run passed.
- Source inspection and `git diff --exit-code 2d8acba...` scoped to old legacy
  versions confirmed no changes to them. Staged changes are only this new
  proposal directory. Final local commit and review artifact IDs are returned
  in the handoff.
- Arithmetic uses Python doubles. No GPU/DCTL compile, Host/Resolve proof,
  visual acceptance, installation, R2 port, skin/gamut/LumaMix redesign, push,
  PR, merge or release occurred.
