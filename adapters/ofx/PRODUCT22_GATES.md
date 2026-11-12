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
-2.2 named binary SS installation/recognition still pending at this checkpoint.
- No automatic v2 or original27-control migration; keyframe/animated state coverage pending.
- Host DCTL evaluation pending; generated DCTL CPU parity is not Host DCTL.
- Wide profile/material/menu/alpha/fallback acceptance, real-time playback and long sustained thermal/memory behavior are not broadly accepted.
- Known Host alpha0 hidden-RGB loss reproduces with pure copy OFX; not a fixed PM bug or full RGBA pass. Extreme finite stress misses ordinary absolute tolerance; do not silently switch tolerance or infer practical footage impact.
- User visual acceptance is bounded to the trial they saw; not every material/operator choice. No formal tag/release/main replacement performed.

## Packaging and rollback
Keep historical internal bundle name. Preserve the entire previous same-ID bundle outside Plugins and its hashes, save/export projects, check no render, close Resolve, replace in vacated path, cold restart and verify actual loaded binary. Never merge two bundles. Restore the preserved bundle and hash to reverse; trial Makeup states should not be overwritten in an older product.

## Automatic build gates
The2.2 feature-branch push CI now runs the existing neutral-Hue reference and Makeup single-protection suites through verify_hud.py on Linux and Windows. The Windows OFX build.ps1 also explicitly executes both CMake test targets before source/package checks, so merely compiling the tests is no longer mistaken for running them. Portable runner records each new suite output and test-source hash separately. These are source/model gates, not Host acceptance or a rebuilt deployed product.
