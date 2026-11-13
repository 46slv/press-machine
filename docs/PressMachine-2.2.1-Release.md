# Press Machine OFX v2.2.1 (Windows x64)

Maintenance release of the 30-control Makeup / Graph 1.5 product. The creative pixel algorithm, control schema, compatibility ID/version 3.1, bundle stem and SDR profiles are unchanged from v2.2.0. The internal v3.curve.dev identifier is intentionally retained for saved nodes.

## Changes
- Mandatory Graph source checks in build/package paths prevent representative missing registrations and descriptors from silently shipping.
- Post-build binary/source hash binding rejects stale or substituted binaries and missing sidecars during packaging. This is consistency checking, not a signature or independent provenance attestation.
- Normal Windows build supports the installed Visual Studio generator rather than assuming VS2019, with explicit/cache conflict checks.
- Added Final overlap/boundary regression coverage. No new Density correction or color-processing feature is claimed.

## Exact artifact
- Source/build commit: 9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4
- Main Linux/Windows CI: https://github.com/46slv/press-machine/actions/runs/43439589124
- ZIP: PressMachine-OFX-v2.2.1-Windows-x64.zip (780352 bytes)
- ZIP SHA256: 8249f98b3d81104be965618d060e02ddba13a5e4850901846e69f43fe7b97ecd
- OFX SHA256: 5f6e0d978f1217c97d0162e99fda98b33fd7a998051eadeafbf027c8242b84b3
- GRAPH_BUILD_BINDING.json SHA256: 7c90e511d80e55de3c0b018c96c67f2778a20bd509e0b4fabe4112324c23fcbb
- Binding covers 18 source inputs. Fresh ZIP extraction and product package verifier passed. The exact tested binary was packaged without rebuilding.

## Bounded acceptance of this binary
On an isolated Windows Resolve environment, a single 206-frame (8.583-second), 3840x2160/24fps camera clip completed both Density 0 and 100 renders, with Chroma 0, Response 2 and other creative controls neutral. Fixed AWG4/LogC4 input to Rec.709/Gamma 2.4 output was used. Density 100 survived save/reload; four Graph panels were visible.
Selected native-size edge and wall crops showed intended darkening with retained texture, without an obvious newly introduced color rim or coarse texture in those inspected regions. This is not a frame-by-frame continuous perceptual verdict.
A separate generated linear Rec.709 fixture confirmed neutral input identity, finite Density output, two colors only at hard complementary boundaries, 800 distinct float ramp values and Graph ON/OFF pixel equality. The relatively bright neutral center in smooth complementary mixtures is consistent with the specified saturation-dependent Density weighting and neutral preservation; no pixel correction was warranted.
Previous projects, settings, render queues and installed bundles were preserved/restored after acceptance. Earlier releases' host receipts are not relabeled as this binary's tests.

## Install and rollback
This is an unsigned manual-install Windows x64 OFX bundle. Download the ZIP and its checksum; compare SHA256 before installation. Save/export projects, ensure no render is running, and quit Resolve. Back up the complete existing same-ID bundle outside every OFX scan path, then replace it at the normal OFX location. Never install duplicate copies of the same ID. Keep the backup for rollback and verify an isolated project before opening production work.
The ZIP contains the OFX binary, third-party notice and Graph build-binding sidecar only. No SDK, footage, NVIDIA runtime, private test material or Graph-less DCTL replacement is distributed. Enable Graph and viewer OpenFX overlays; Graph is not baked into rendered pixels. v2/V21 and older release assets are not replaced.

## Limits
Continuous perceived flicker, long playback, sustained/realtime 4K performance, all footage/lighting/skin conditions, HDR/alpha and every backend remain unverified. Numeric equality and selected still crops do not prove absence of temporal artifacts. Source legal/full interpretation was held fixed, not calibrated as a scene-referred oracle. Source camera metadata can persist on transformed EXR; communicate the actual output profile explicitly. No new PQ/HLG, tone/gamut mapping or range conversion is introduced.
This maintenance release is accepted for the stated representative scope; it does not close all broader visual/performance research gates.
