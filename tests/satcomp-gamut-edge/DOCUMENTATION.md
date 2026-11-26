# Press Machine: documentation and evidence map

This page links the implementation, product guidance and validation records. A test result belongs only to the exact build, host path, and inputs described by its receipt.

| Scope | Reference | What it does not establish |
| --- | --- | --- |
| Press Machine product, operation, and installation | [Product README on main](https://github.com/46slv/press-machine/blob/main/README.md), [Japanese quick guide](https://github.com/46slv/press-machine/blob/main/docs/PressMachine-2.2-Quick-Guide-JA.md), [2.2.1 release notes](https://github.com/46slv/press-machine/blob/main/docs/PressMachine-2.2.1-Release.md) | A limited product gate is not a full range, real-time, or source-footage guarantee. |
| Revision 3 design and implementation | [Current comp/hue/density contract](https://github.com/46slv/press-machine/blob/main/docs/PressMachine-vNext-Comp-Hue-Density-Spec.md), [historical implementation and qualification PR #9](https://github.com/46slv/press-machine/pull/9) | Historical 27- or 29-control designs do not replace the newer product contract. |
| Graph HUD | [Graph viewport and Release placement PR #11](https://github.com/46slv/press-machine/pull/11), [placement check](https://github.com/46slv/press-machine/commit/b10253d4a521e7d117f35de397e1d02a4f985659) | Build or CPU layout success alone is not exact Resolve display acceptance. |
| Original design documents and legacy DCTL | [Nine design documents](https://github.com/46slv/press-machine/commit/d7af617b012e3f43c4ca95f35a5f48087102464f), [two original DCTLs](https://github.com/46slv/press-machine/commit/75a9fbfbe0f8cfb328257f27dda3ec0eb8d3f936) | Historical designs are not current requirements. |
| SatComp | [Offline conversion/edges](README.md), [near-DI](di-route-r2/README.md), [old Color host diagnosis](resolve-final/SATCOMP-RESOLVE-FINAL.md), [21.2 route comparator](evidence/resolve-21-2-sc12.md), [independent Edit OFX r3 acceptance](resolve-edit-r3/README.md) | Neither fixed Edit acceptance nor offline DCTL success corrects the known extreme-input failure of the older Color ResolveFX. |
| Reference grade | [Blue shade / cream sunlight](look-reference-ryo-ichikawa.md) | This is an analysis of two rendered reference stills, not original grade settings, a preset, or a measured footage match. |

## Portable handoff notes

- Preserve known behavior and label artifacts with exact source, binary hash, host version, adapter, GPU, color management, inputs and controls. A validated source generator or CPU reference does not automatically qualify the generated DCTL or an installed OFX on Resolve.
- For a revision-wide acceptance, move from deterministic scalar and adapter checks to the actual host: load controls, apply an active effect, export comparable frames, save and reopen, and re-export. Compare bypass and control captures before interpreting an active difference. Then do ordinary footage, visual and performance checks, including sustained playback and the intended output format.
- For performance investigations, compare the same clip, timeline, cache state, viewer scale, effect settings and device. Separate UI playback observations from timed exports and GPU telemetry. Remove provably redundant work first; compare the visual and numerical consequences of changes before adopting a faster expression.
- Preserve production media, raw render packages and private work logs separately. This public index intentionally does not republish private Notion material, raw internal logs, binary evaluation packages, or third-party reference stills. The public evidence is an auditable technical subset, not a raw mirror.
