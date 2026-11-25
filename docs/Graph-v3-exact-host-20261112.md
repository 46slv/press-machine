# V3 Graph integration: bounded exact-build Host verification

2026-11-12. Supersedes the unrun Host gates in Graph-viewport-candidate-20261112.md. This is engineering verification, not owner acceptance or a release.

## Source and compatibility

Current published main is v2 (9cd6158779484e43e88ad11fd7d08994ea4f5e2b), not the v3 integration target. Do not apply the entire v3 branch to main as a Graph-only change.

The v3 baseline dev/reuse-v3-graph-isolated-20261111 at 6c8748c7241d6d7c33a767fea8c84fe7731d1a58 already includes the Graph descriptor, V1 overlay registration, HudModel/DensityGraph, 29-parameter redraw slaves and opengl32 linkage. The integration candidate fix/graph-viewport-20261112 at 2fc5e0027d167b62597427df38b31be71cb7f9d1 adds only viewport placement and its regression tests/docs/receipts: nine files, 60 additions, 12 deletions. No pixel-processing code, processing parameter identifiers/defaults/order, plugin ID or version changes. Frozen-source separation passed for 16 files; focused CPU 75,877, alpha 77, HUD model 12,129, Density graph 5,434, placement eight and luma curve checks passed on Windows.

## Distinct binaries

- Preserved installed v3: com.46slv.PressMachine.v3.curve.dev, version 3.1; SHA256 421fdeadb89b06037dae64e6efb213b7ec8fe39e71983e9732b54092d69aec30.
- Exact candidate: same ID and version; SHA256 1ba0c188abd7152894afe37f3549d741773ca8d793e2f3e87205120e7b9801c8. This is the product-identity build tested below, not the QA-identity binary.
- Earlier side-by-side QA: com.46slv.PressMachine.graph.viewport.qa.20261112, version 3.1; SHA256 042fa9bb774a29d338bd8df437f9f3c33ff2082057d51019cc0d5a77dace952b. Those results alone are not exact-binary verification.

No active git/compiler writer was found on CDs. The independent checkout was used. Original project was saved/exported and no render was active. To avoid duplicate IDs or overwriting, Resolve was closed, the installed v3 bundle was moved intact outside the scan path, and the exact candidate was copied to its vacated path. After testing, the candidate was archived and the preserved original was moved back with its original SHA verified. No existing OFX bytes were overwritten.

## Host observations

Independent project PM_Graph_Viewport_Independent_20261112_01, INSTALLED_421FDEAD_COMPARE timeline originally saved with the installed v3 identity:

- Full cold launch with exact candidate loaded the existing node and saved Graph ON settings without a missing-plugin prompt.
- Resolve initially selected Qualifier viewer mode. OpenFX Overlay selection was required; then all four panels displayed. This host mode is independent of the Graph checkbox and cannot be forced by the plugin draw callback.
- At 25% zoom the exact candidate retained all four panels; the preserved installed binary had previously hidden them at this zoom with Graph ON and OpenFX overlays enabled.
- Graph OFF removed the panels; ON restored them.
- Luma Width 0.5 updated the Graph. Graph ON and Width 0.5 were saved/exported, another project loaded, then the QA project reloaded: both values and the four panels persisted.
- ON and OFF were separately rendered as one 800x1000 RGB float EXR at the same frame and default processing settings. Both jobs completed 100%. Whole files were byte-identical: 9,616,590 bytes, SHA256 2f18582d086bfcf582cab84cdca5a61c3835dca81bb3be014747560850f9d072. This is exact-file equality, not a decoded RGBA comparison.

The original incident's exact instance/settings remain unknown. Two bounded non-display gates are established: host OpenFX overlay mode and old image-bound placement suppression. No claim that either was the owner's precise original cause.

## Remaining release gates

All 29 controls in Host, broad image/parameter ranges, performance, and physical GL viewport below the minimum are not fully accepted. No v2 backport, main merge, release or owner acceptance was performed. The exact candidate is archived; original installed v3 was restored. A deliberate v3 product update can use this candidate without retransplanting Graph or mixing in newer Hue-processing experiments. Preserve OpenFX Overlay usage guidance with any distribution.
