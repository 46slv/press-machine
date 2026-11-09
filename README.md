# Press Machine

Color processing shared by DCTL and OpenFX adapters.

- Windows OFX v2.0: skin-reference Hue zero, 25 controls, CPU/CUDA rendering. See [release and installation notes](docs/PressMachine-v2.0-Release.md).
- [OFX source and build](adapters/ofx/README.md).
- Preserved red-zero DCTL baseline: adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl.
- Shared math: core/press_machine. Stable parameter schema: parameters/press_machine_v2.json.
- [Architecture and backend coexistence](docs/PressMachine-v2-architecture.md).
- [vNext Comp → Hue → Density implementation specification](docs/PressMachine-vNext-Comp-Hue-Density-Spec.md) — v3.dev source integration candidate; Host acceptance remains pending.

DCTL and OFX remain in this repository with separate artifacts and validation receipts. Legacy projects are not automatically migrated. The graph HUD and expanded masks are separate work, not part of v2.0.

Download published artifacts from this repository's Releases page. Review the exact artifact hashes, requirements and known limits before installation.

Current Revision 3 source lane: [Draft PR #9](https://github.com/46slv/press-machine/pull/9), head `53f074b12d3b05ad23fd830e152d6c89c8434787`. `parameters/press_machine_v3.json` defines 27 controls for the separate `com.46slv.PressMachine.v3.dev` candidate. Angle / Pattern / Strength plus independent Hue Bias and Luma Split follow Comp → Hue → Density. Focused cloud qualification is passing; target Windows CUDA/OFX/Resolve and visual/4K acceptance remain candidate-specific open gates. Released v2 schema, DCTLs and acceptance evidence remain unchanged. See the vNext spec and OFX README for exact boundaries.
