# Press Machine

Color processing shared by DCTL and OpenFX adapters.

- Windows OFX v2.0: skin-reference Hue zero, 25 controls, CPU/CUDA rendering. See [release and installation notes](docs/PressMachine-v2.0-Release.md).
- [OFX source and build](adapters/ofx/README.md).
- Preserved red-zero DCTL baseline: adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl.
- Shared math: core/press_machine. Stable parameter schema: parameters/press_machine_v2.json.
- [Architecture and backend coexistence](docs/PressMachine-v2-architecture.md).

DCTL and OFX remain in this repository with separate artifacts and validation receipts. Legacy projects are not automatically migrated. The graph HUD and expanded masks are separate work, not part of v2.0.

Download published artifacts from this repository's Releases page. Review the exact artifact hashes, requirements and known limits before installation.
