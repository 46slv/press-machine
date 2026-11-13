# Preserved Press Machine OFX v2.0 reproduction

Current main builds Press Machine2.2 using the retained v3.curve.dev compatibility ID. Do not use its current build scripts to reproduce the earlier v2.0 binary.

The existing public release/tag `ofx/v2.0.0` remains at commit `9cd6158779484e43e88ad11fd7d08994ea4f5e2b`, with its original release assets unchanged. Use an independent checkout of that tag/commit and its own README/docs/PressMachine-v2.0-Release.md for the v2.0 SDK/toolchain/build procedure. A new build is not assumed bit-reproducible across toolchains: use the original hashed release ZIP when exact binary identity is needed.

Example isolation: `git worktree add --detach ../press-machine-v2-repro ofx/v2.0.0` after fetching that tag. This does not migrate nodes or install anything. Current v2 schema and immutable19382145 DCTL are preserved byte-for-byte. The2.2 bundle name and pluginID differ from releasedv2; replacing2.2 must never overwrite the v2/V21 bundles or their existing projects.
