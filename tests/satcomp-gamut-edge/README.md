# Standalone SatComp DCTL: gamut and soft-edge verification

Status: CPU candidate only. Not a release, not an OFX change, and not qualified in Resolve. The standalone DCTL retains the eight controls and existing creative saturation behavior.

## What changed

- When the input and output primaries are the same and the creative operation does not change the pixel, encode directly from the input-linear channels. A transfer-only change must not make an unnecessary round trip through a different gamut.
- Factor the scale into LogC3/LogC4 power evaluation so representable values do not fail because of an avoidable intermediate overflow.
- Preserve the existing out-of-domain passthrough contract: invalid selectors, non-finite input or genuinely unrepresentable arithmetic can return the original RGB. If profiles differ, that fallback is not output-profile RGB. No clipping or claim of arbitrary signed/HDR reversibility. A true gamut change can lose low-amplitude channels when the intermediate format rounds them away.

## Reproduce

On Windows, use an existing Python 3.12 and MinGW-w64 g++ toolchain. No dependencies or host settings are modified. Run from the repository root:

    python -B tests/satcomp-gamut-edge/replay.py --cxx <path-to-g++> --out <new-scratch-dir>

The runner verifies the source SHA-256s, compiles both complete DCTLs (g++ 15.2.0 in the captured run, float32, no fast math or contraction), requires RED to fail for the intended reasons, and replays GREEN, the edge tests, and the prior UI/behavior checks. An independent Decimal-75 reference reconstructs color transforms and compares the actual compiled RGB entry. Raw deterministic logs and CSV are in [evidence](evidence/); there are no media or binary dependencies.

| Check | Result |
| --- | --- |
| Old source, same-gamut and finite-range regression | 1,316 pass / 64 expected failures |
| Fixed source, same suite | 1,380 pass / 0 fail |
| Prior behavior/selector checks | 1,681 pass / 0 fail, including eight UI declarations |
| Edge suite | 70,160 assertions; 180 aggregated metric rows, not 70,160 fixtures |
| Ordinary blurred ramps | Maximum candidate-vs-old difference 1.86e-9; no spatial spread in the synthetic tests |
| Synthetic extreme HDR ramp | LogC4/LogC3 maximum error against reference 9.54e-7 / 1.91e-6; removes discontinuity where old code returned raw Linear RGB despite log output |

For an AP1 LogC4 pixel of (-2, .1, 4), transfer-only AP1 Linear preserves red and green after the fix. A real AP1 to DWG to AP1 round trip still cannot recover channels that were lost while storing the highly imbalanced intermediate as binary32. See RED/GREEN and edge metrics for the reproducible tests.

## Historical evidence and current host gate

- A different eight-control standalone SatComp, SHA-256 143c0f0d198f0949ca68ed62b97a9d70cc8ff537951cabaded0c3b90bd219d86, was loaded on Windows DaVinci Resolve 21.1.0.14 on 2026-11-08 JST. The log records all eight controls, visible edits, bypass toggling, and settings retained after a normal reopen of a scratch project. This was not numeric or export qualification. It does not qualify this candidate.
- An older Density R4 CPU experiment used blurred edges from real footage. That was Density, not evidence that this standalone SatComp behaves on the same Resolve timeline.
- On synthetic soft edges, compositing encoded log can generate much larger differences than linear compositing, including when bypassed. The standalone DCTL sees only current-pixel RGB, with no alpha or neighbors. Do not add a blur or claim to repair premultiplication inside this entry point.

Still required in a disposable Resolve project, on this exact file: compile and read back all eight controls, compare candidate vs baseline and bypass with identical color selections and same frame, include sign/HDR and alpha-edge clips, reopen and rerender or export, then log version, GPU, project color pipeline and measurements. If using stacked effects, compare SatComp only, Density only and both off. Distinguish any existing RGB/compositing artifact from a SatComp regression. Do not present CPU results as Resolve host evidence.
