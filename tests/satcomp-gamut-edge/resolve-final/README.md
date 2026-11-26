# Review bundle

This directory records a scoped diagnostic, not a shipping change. Base: Draft #19, `769a014c22c5d857fd771a659672171340a753b1`; the original eight-control ResolveFX route is **RED** on the tested host. No runtime asset is changed by this local review commit.

- [判定・再現手順](SATCOMP-RESOLVE-FINAL.md) / [タスク台帳](SATCOMP-TASKS.md)
- The EXRs and independent-decoder replay helpers live in the companion `SatComp-PR19-Resolve-final-diagnostics.zip`, 156 entries, SHA-256 `68b32eabea360a9d8debf3ca64e43984b213c9a14d292a335fa083ec99990b44`. Its six measurement commands were rerun from the extracted archive and produced the archived metrics and CSVs byte for byte. Run measurements from the extracted root, not this evidence-only repository directory.
- The DI near-range replay is in `SatComp-PR19-DI-route-R2.zip` (separate companion); see [near-DI report](DI-ROUTE-R2-REPORT.md).
- The CUDA constant probe source is here for code review only, not a product OFX. The `gpu-verification-final.json` is the standalone device check; the Resolve render and exact output comparison are in `evidence/sc09-final.json` and the companion archive.
- Separate follow-up: [Windows Resolve Studio 21.2.0.6 Edit clip OFX evaluation](../resolve-edit-r3/README.md). The Edit result does not change the RED verdict for the original Color ResolveFX route.
