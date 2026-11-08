# Press Machine v2.0

Windows x64 OpenFX color tool with Hue Angle zero anchored to the existing skin-chart reference. The OFX and DCTL adapters share their color math. All 25 controls remain; new controls, expanded masks and the optional graph HUD are outside this release.

## Install or update

1. Save your Resolve work and finish any render. Close Resolve normally.
2. Extract the release ZIP. Verify its SHA256 and the included SHA256SUMS.txt.
3. Back up any existing PressMachineV2SkinAxis.ofx.bundle outside every OFX plugin search directory.
4. Copy the entire PressMachineV2SkinAxis.ofx.bundle to C:\Program Files\Common Files\OFX\Plugins. Windows may ask for administrator approval. Keep the bundle and module names unchanged.
5. Start Resolve normally. Find Press Machine v2.0 under the Press Machine group.

The release keeps identifier com.46slv.PressMachine.v2.skinaxis and OFX version 2.0. It replaces the earlier SkinAxis TEST bundle in place. Do not install a second copy of that identifier in another plugin directory. Preserve the backup for rollback, but keep it outside OFX search paths. The original red-zero OFX has a different identifier and can coexist.

The companion PressMachine_v2_0_SkinAxis.dctl is optional. Copy it to your own DCTL location without overwriting your existing DCTL. Its bytes are the qualified SkinAxis native artifact; the 19382145 red-zero baseline remains separately available in this repository.

## Color setup

Match Input Primaries and Input Transfer to the signal entering this node. Same as Input output settings retain that profile. OFX does not automatically infer your timeline/node color management.

Hue zero is the existing D65 sRGB (194,150,130) skin-chart direction mapped into the active CF2 linear BT.2020 plane. It is not every skin hue, an Oklab mask locus, or a promise of exact vectorscope-line alignment.

To translate a legacy red-zero physical target: newAngle = wrap360(oldAngle - 26.120959577861925). Do not round to the displayed slider step. Existing nodes, presets and animated keys are not automatically converted; independent wrapping of keys can change interpolation. Keep legacy projects on their original plugin when exact reproduction is required.

## Requirements and known limits

- Validated on Windows x64, DaVinci Resolve 21.1 build 14, RTX 3070 Ti and its NVIDIA CUDA driver. CPU rendering is supported when the Host uses the CPU backend; automatic recovery from a CUDA failure is not provided. This is an unsigned manual-install package.
- CUDA uses the Host stream. The driver must support compute_75 PTX and CUDA context IDs. No CUDA toolkit is needed at runtime.
- Other operating systems, OpenCL/Metal, other Resolve versions and Free/Studio cross-edition compatibility are not verified.
- Strong Hue, especially one Point, can increase chroma, tint neutrals and produce out-of-gamut values. No new clipping repair or gamut mapper is included.
- Group headings collapse and expand. Resolve may reopen groups after a node switch; parameter values remain independent of that UI state.
- SkinAxis long-run speed and broad footage qualification are not established. Earlier short observations from another OFX artifact are not a performance promise for this release.
- Diagnostics append at most a few startup/backend records to %LOCALAPPDATA%\PressMachine\OFXv2-test.log and the Host's non-popup log. The release marker is release=2.0.0. The retained filename supports existing diagnostics; it does not mark the release as a trial.
- No automatic updater, installer, project migration, new controls, expanded skin masks or graph HUD is included.

See RELEASE_MANIFEST.json for the exact binary/core/DCTL hashes and candidate-specific verification scope. A CUDA enqueue log proves dispatch, not completed output; completed-frame comparisons are recorded separately.

The linked OFX Support Library's redistribution notice is inside the bundle. SDK, NVIDIA runtime and driver binaries are not bundled. This release does not introduce a new license for Press Machine source.
