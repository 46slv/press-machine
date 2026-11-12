# Press Machine 2.2 qualification boundary

User selected the public name2.2 after trying the Makeup/Graph1.5 candidate. This is forward-use approval, not evidence that every technical gate passed.

## Compatibility contract
- Public descriptor label: Press Machine2.2 (with a space in the actual label).
- Preserve internal ID `com.46slv.PressMachine.v3.curve.dev`, major/minor3.1, and internal bundle/binary stem. Existing trial nodes identify the plugin by these keys, not its public product name. No major downgrade, ID substitution or duplicate install.
- Schema30, defaults, ranges, option indexes, Graph and all CPU/GPU/DCTL math remain identical to the tested Makeup candidate. Only descriptor label/description changed.
- Released v2 and V21 remain separate, untouched. Old v2 states are not automatically converted. Trial node compatibility is not a general cross-ID migration promise.

## New exact-build evidence
- Binary75799ec745badc5219909dd35afcf494a9a28fb304eed4bd7cbbd2319eb75251.
- Exports ID/version unchanged. Source separation assertion freezes processing classes and Graph implementation; core/schema/generated/PTX unchanged.
- Cold restart then imported existing Makeup150/Skin100 trial DRP as independent project. Actual2.2 descriptor, Pre120/Comp40/Makeup150/Skin100 and Tetradic45/Strength50/Bias-25/Split100 retained. Four Graph panels and neutral-Hue curve appeared after OpenFX overlay selection.
- One800x1000 RGB FLOAT Host output: entire scanline payload equals fe11629a candidate output; only proimCameraID header differs. Project save/load retains visible nonneutral values and Graph. This is a static saved-state case, not animated/keyframe coverage.

## Existing evidence retained, not rerun
Makeup raw-chain/single-skin oracle; CPU/generated-DCTL CPU/CUDA parity; old29 at Makeup100 bit-exact; limited old29 Host load/GraphON-OFF; SS recognition of fe11629a; short unique4K206frames. See MAKEUP_HUD150_CANDIDATE.md. Those artifacts have their own exact hashes and are not relabeled as fresh2.2 Host tests.

## Open gates and known limits
-2.2 named binary SS installation/recognition complete with saved original project/settings/timeline/jobs and reversible backups; no new SS render/pixel gate.
- No automatic v2 or original27-control migration; keyframe/animated state coverage pending.
- Current generated DCTL has limited actual built-in Host default/active and Density/LookSkin evidence; wide profile/range/motion/alpha/Final-active conditions remain open. Generated DCTL CPU parity alone is still not Host DCTL.
- Wide profile/material/menu/alpha/fallback acceptance, real-time playback and long sustained thermal/memory behavior are not broadly accepted.
- Known Host alpha0 hidden-RGB loss reproduces with pure copy OFX; not a fixed PM bug or full RGBA pass. Extreme finite stress misses ordinary absolute tolerance; do not silently switch tolerance or infer practical footage impact.
- User visual acceptance is bounded to the trial they saw; not every material/operator choice. No formal tag/release/main replacement performed.

## Packaging and rollback
Keep historical internal bundle name. Preserve the entire previous same-ID bundle outside Plugins and its hashes, save/export projects, check no render, close Resolve, replace in vacated path, cold restart and verify actual loaded binary. Never merge two bundles. Restore the preserved bundle and hash to reverse; trial Makeup states should not be overwritten in an older product.

## Automatic build gates
The2.2 feature-branch push CI now runs the existing neutral-Hue reference and Makeup single-protection suites through verify_hud.py on Linux and Windows. The Windows OFX build.ps1 also explicitly executes both CMake test targets before source/package checks, so merely compiling the tests is no longer mistaken for running them. Portable runner records each new suite output and test-source hash separately. These are source/model gates, not Host acceptance or a rebuilt deployed product.

## Current generated DCTL, actual built-in Host checkpoint
Exact generated DCTL ae50fc47726103e12041186a287c4f3ef0580c3074092c86993ecae7942121ca was copied unchanged under a unique QA name, selected in Resolve built-in DCTL on CDs, and exposed the30 controls. RefreshLUTList alone did not update its effect menu; a saved, render-free restart did. Default and active800x1000 RGB FLOAT still frames completed. Default entire2,400,000 RGB words exactly equal original inputRGB. Active Pre120/Comp40/Makeup150/CompSkin50/Angle45/Strength50/Bias-25/Split100, Complementary, DWG/DI/outputSame, other stages neutral: allRGB finite;1,892 sampled pixels versus CPU core max5.960464477539063e-8 (ordinary2^-13 threshold). Active controls persisted across project save/load. This is real built-in Host DCTL, not generated-DCTL-as-CPU. It is not all-pixel active parity, alpha, all profiles/ranges, Density/Final active, long playback or full product acceptance.

Source/core/OFX unchanged; original project settings/timeline/14jobs exact and no render; original1ba OFX unchanged. Unique QA DCTL moved outside LUT scan after preservation; old LUTs untouched. SS/WS not accessed. This narrows the open HostDCTL gate to wider conditions rather than claiming full completion. It does not select a new Hue operator or automatically declare all nonDensity gates closed.
