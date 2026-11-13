# Current branch: Press Machine 2.2

This is the current **30-control Makeup + Graph1.5 product** with append-only SDR color profiles, not the historical29-control checkpoint below. Public name2.2 retains the trial OFX identity/version for saved-project compatibility; it does not replace released v2 or automatically migrate old nodes. The release target is `ofx/v2.2.0`; documented limited checks are not full-domain acceptance.

- [Implemented SDR gamut/transfer definitions and exact Host scope](docs/PressMachine-2.2-Input-Rec709.md), [preserved v2 reproduction](docs/PressMachine-v2-Reproduction.md).
- [Current2.2 contract](docs/PressMachine-vNext-Comp-Hue-Density-Spec.md), [Japanese usage guide](docs/PressMachine-2.2-Quick-Guide-JA.md), and [exact-build evidence / open gates](adapters/ofx/PRODUCT22_GATES.md).
- Current [generated DCTL](adapters/ofx/generated/PressMachine_V3_Curve_TEST.dctl): SHA256 `5045b4164f101101ca1468866657e0901f5fb340388a47fcabf6b312e26f27fc`,30 controls including Makeup Saturation. The new-profile DCTL is generated/CPU-tested reference only, not newly Host-qualified or included in the OFX release. The historical v3 TEST filename/comment is retained; the old DCTL hash below describes the historical checkpoint only.
- **Graph is mandatory in OFX and is OFX-only**: variable swatches, neutral-Hue reference curve and four-panel auto1.5. Enable OpenFX viewer overlays. The reference DCTL has no Graph and is not a complete substitute for the requested OFX product.
- [Limited actual built-in DCTL / Density interaction](adapters/ofx/PRODUCT22_DENSITY_INTERACTION.md) is distinct from OFX acceptance. Look Skin protects combined Hue+Density; no new Hue formula or research Density/mask model is adopted.

---

## Preserved historical branch notes

# Provisional 29-control curve candidate

This branch adds adjustable **Luma Pivot EV** and **Luma Width** to the separate TEST candidate. The default 0/1 pair preserves the original luminance response. Set Luma Split away from zero to explore the curve. Final shape and ranges remain provisional.

- [Design, controls, measured scope and limits](docs/PressMachine-Luma-Curve-Prototype.md)
- [Generated DCTL](adapters/ofx/generated/PressMachine_V3_Curve_TEST.dctl), SHA-256 `8c9ebcb72295d60877f300d5ddb863d629b565cb0be11deb984e5f1b77bafad6`
- [Reused Graph HUD source candidate and pending Host gates](docs/PressMachine-Graph-HUD-Migration.md)
- [Current build instructions](adapters/ofx/README.md#current-29-control-candidate)
- [Limited native DCTL evidence](adapters/ofx/results/v3_curve/HOST_DCTL_LIMITED.json)

Original 27-control v3 and released v2 artifacts remain separate. The retained baseline notes below do not describe the build target of this branch. This is not an accepted release.

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

Current Revision 3 source lane: [Draft PR #9](https://github.com/46slv/press-machine/pull/9). Source implementation baseline is commit `c32d6dc1952c4a8c87053d3f757f57613bd91a4b`; the expanded focused qualification suite is present from `95c8ed1fa709db1f6104a40e74a3f2484e01748e`. Later commits on the PR may be documentation-only; use the live PR head for the exact branch snapshot. `parameters/press_machine_v3.json` defines 27 controls for the separate `com.46slv.PressMachine.v3.dev` candidate. Angle / Pattern / Strength plus independent Hue Bias and Luma Split follow Comp → Hue → Density. Focused cloud qualification is passing; target Windows CUDA/OFX/Resolve and visual/4K acceptance remain candidate-specific open gates. Released v2 schema, DCTLs and acceptance evidence remain unchanged. See the vNext spec and OFX README for exact boundaries.
