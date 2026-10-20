# Approved A2 prototype task log

## 2026-10-20 — authorization and isolated branch

- Parent supplied the user's explicit approval of the recommended A2 prototype
  and authorized local implementation, focused verification and a private
  Library package. The approved mathematical basis is commit
  `7e1870cc5a2690d72f37653b39c899c5e6a284b0`.
- Requested model: `gpt-6.1-sol`; actual runtime ID **UNVERIFIED**. No model
  substitution, fan-out, or status request to another agent occurred.
- Checkout was clean at that exact proposal commit with one worktree. New
  local branch `prototype/press-machine-a2-20261020` was absent before creation.
  This task is its sole observed writer. Older candidate/proposal refs and
  files are preserved.
- Read source, approved proposal, shared debugging/Git owners and repository
  instructions. No AGENTS.md was found in this checkout.

## Implementation

- Created a separate `legacy/a2-prototype` directory and DCTL with distinct
  prototype title/name. No v1.2.3 release identity was assigned.
- Implemented exact approved A2 with an analytic gain for each branch.
  Transform and graph use the same helper. Removed the old norm division and
  hard chroma discard; Sat Density uses actual continuous scalar output.
- Preserved all unrelated source payload, creative stage order and UI meanings.
  No B/C substitution, R2 port, skin, gamut, encoding or Luma Mix policy change.

## Verification and package preparation

- `python -B -m unittest discover -s "Press Machine/legacy/a2-prototype/tests" -v`
  passed all 12 focused tests on the first run (0.043s, OK). One method also
  passed all five retained v1.2.1 contracts against the prototype.
- Actual-source tests cover analytical branches, zero/near-zero and threshold
  boundaries, no-ops, ordinary legacy settings, source scope and graph sharing.
  Binary32 scalar edge probes include representable values around boundaries
  and subnormals; they do not certify GPU behavior.
- Direct old/new DCTL comparison showed only the intended helper and usage
  changes. `git diff --exit-code` against the proposal baseline before staging
  confirmed every existing tracked file unchanged.
- Added source-linked usage/change notes, reproducible test instructions,
  numerical results and Linear patch cases for later user-controlled review.
- Final package is assembled from the clean commit, with only relevant source
  fixtures and a byte manifest. It is checked by running the same suite from
  an extracted copy, which verifies that its test dependencies are included.
- Commit, package validation outcome, ZIP hash and native Library file ID are
  supplied in the final handoff. No installation/Resolve, public push, release,
  PR, main merge, force push or security change occurred.
