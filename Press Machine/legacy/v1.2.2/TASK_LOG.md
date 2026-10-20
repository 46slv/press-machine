# Legacy v1.2.2 neutral Density task log

## 2026-10-20 — source and ownership

- Requested model: gpt-6.1-sol. Runtime model ID could not be verified in this execution environment; no model substitution or delegation was invoked. The initial progress message incorrectly presented that ID as verified and was corrected before delivery. No other Codex agents were queried or used.
- Fresh isolated clone: `C:/Users/shiro/Documents/Codex/2026-10-20/task-4/press-machine`.
- Authorized remote: `https://github.com/46slv/press-machine.git`.
- `git ls-remote --heads` confirmed source branch `fix/press-machine-legacy-v1-2-1` at accepted SHA `430aa1528c55abedfc6328cec6873432a374f27d`; the new task branch was absent.
- New local branch: `fix/press-machine-neutral-density-task4-20261020`. Before creation the ref was absent locally, this clone had one worktree, and repository inspection found no AGENTS, writer claim, or ownership lock files. This fresh branch has no observed competing writer; other checkouts were not modified.
- Read repository README, legacy preservation/fix record, migration/algorithm requirements and relevant source. No repository AGENTS.md found. Shared routes: `~/.agents/knowledge/shared/coding/debugging.md` and `git.md`.
- v1.2 -> v1.2.1 diff confirms Density and compression are identical; only header, LogC4 equations and graph identity changed.
- Baseline: `python -B -m unittest discover -s "Press Machine/legacy/v1.2.1/tests" -v` — 5 tests passed.
- Sandbox DNS initially failed for GitHub. Normal authorized Git access succeeded with the network permission route; no credentials or security settings changed. A read-only CIM process listing was unavailable; ownership evidence comes from fresh checkout/ref/worktree and repository checks instead.

## Decision

This is a scalar semantic regression: the legacy knee returns a positive saturation at zero input, but reconstruction emits zero chroma for `sat_in <= 1e-6`. Sat Density nevertheless darkens luma with that unrepresentable saturation. Use the existing reconstruction guard for the Density input only. Preserve Dynamic Density, knee, Threshold/Ratio mapping, Makeup, Luma Mix extrapolation, signed decomposition, graph and encodings. Full continuity beyond the guard needs a separate curve decision.

The new core docs explicitly exclude legacy Density and redesign the knee; they do not authorize importing that formula into a maintenance fix. `docs/MIGRATION_NOTES.md` explicitly retains the extreme-small-chroma guard. `legacy/v1.2.1/FIX_RECORD.md` records the creative response as unchanged.

## Regression work

Created a separate v1.2.2 copy; v1.2.1 and archived sources remain unchanged. Added source-executed scalar probes before applying the fix. The unfixed copy ran 7 test methods with 8 failing assertions/subtests; the neutral luma regression, inclusive near-neutral guard, intentional Luma/Dynamic interaction and missing source guard failed as expected. Nonneutral/no-op and retained LogC4/graph contracts passed.

Applied only `sat_for_density = (sat_in > 1e-6f) ? sat_out : 0.0f` to the Sat Density attenuation input. At Y=0.18, T=0.25, K=0.1, R=4, Makeup=1 and Sat Density=1, original `sat_out=0.005996346474` darkened neutral Y to `0.177866896920`; the corrected variant returns Y=0.18 and zero chroma. Pre-Saturation 3 and Makeup 2 probes still respect the original-input reconstruction guard.

## Final verification checkpoint before local commit

- `python -B -m unittest discover -s "Press Machine/legacy/v1.2.1/tests" -v` — 5 tests passed, exit 0.
- `python -B -m unittest discover -s "Press Machine/legacy/v1.2.2/tests" -v` — 7 tests passed, exit 0; includes all 5 existing v1.2.1 contracts rerun against the new source.
- `git diff --exit-code 430aa1528c55abedfc6328cec6873432a374f27d` before staging the new directory — exit 0; every existing tracked file is unchanged.
- `git diff --cached --check` — exit 0. Only four new files under `legacy/v1.2.2` are staged.
- Direct old/new DCTL comparison and the test's full non-header payload comparison confirm the sole equation change is the Sat Density guard.
- Added `FIX_RECORD.md` with source rationale, exact commands/results, numerical boundary probes, test limitations and the remaining curve decision.
- Residual boundary: just above `1e-6`, output chroma remains `0.005997077100` and Y `0.177866640092`. The new guard also causes a luma step here. Continuous correction of chroma and Density above the guard remains separate design work; no taper or knee formula was invented.
- Tests use Python double arithmetic on translated source statements and retained source contracts. GPU/DCTL/Resolve behavior is not certified. No push, PR, merge, release, installation, Resolve operation, credential/security change, or R2 port was performed.
- Existing Git identity was present; local commit outcome and SHA are supplied in the final handoff.
