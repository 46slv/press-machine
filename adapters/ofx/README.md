# Press Machine v3.dev development candidate

This branch implements the separate Comp → Hue → Density candidate with 27 controls. The new schema is `parameters/press_machine_v3.json`; no v2 node, preset, menu index, or saved state is migrated. Pattern choices are Mono, Analogous, Complementary (default), Split Complementary, Triadic and Tetradic. Hue Bias ±100 and Luma Split ±300 remain active at Strength zero. Comp Skin Protect covers conditioning; Look Skin Protect covers Hue plus Density.

Identity: `com.46slv.PressMachine.v3.dev`, version 3.0, label `Press Machine v3.dev`. Bundle and binary stem: `PressMachineV3Dev`. The name intentionally distinguishes this unqualified development candidate from released v2.0.

## Build and verification

Run `python regenerate.py` and `python generate_descriptors.py`. The schema generates the common parameter layout/defaults, OFX descriptors/value mapping and DCTL controls. `regenerate.py` emits `generated/PixelCore.hpp` and `generated/PressMachine_V3_Dev_TEST.dctl`; v3 generation hashes go to `SOURCE_MANIFEST_V3.json`. The immutable v2 DCTL, schema and historical evidence are never rewritten. Do not copy generated output over an accepted artifact.

On the qualified Windows SDK toolchain, `build.ps1` generates sources, compiles NVRTC/C++, runs package checks, focused vNext tests and v3 alpha tests. Output: `build/PressMachineV3Dev.ofx.bundle/Contents/Win64/PressMachineV3Dev.ofx`. No SDK installation is performed by these scripts. Build, compile and Host receipts must be collected anew for this candidate.

`tests/NativeV3.cpp` exports the shared CPU adapter and a CPU-compiled generated DCTL reference. This catches UI-to-core wiring and numeric differences under the same C++ compiler; it does not establish Resolve DCTL compilation or CPU/CUDA parity. Use `tests/verify_vnext.py` for the focused candidate tests. The old `Native.cpp`, `verify_cpu.py`, `verify_skin_axis.py` and original verifiers are v2 historical/reference harnesses and must not be run against the v3 parameter ABI. Old 25-value vectors are incompatible with this 27-value schema.

After coordinating GPU ownership, use `tests/verify_cuda_v3.py` and `tests/verify_cuda_adapter_v3.py` for the candidate CUDA paths. `verify_alpha_v3.py` and `verify_package_v3.py` likewise write only to `results/v3/`. No v2 receipt establishes candidate correctness.

Pending acceptance: Resolve compile/load, all 27 UI values and persistence, completed-frame DCTL/OFX CPU/CUDA comparisons tied to hashes, representative footage and same-condition 4K performance. Do not install or publish this as an accepted release before those gates.

## Historical v2.0 notes (not candidate acceptance)

The following retained notes describe v2.0 only. Old paths, commands and claims below are historical and do not apply to v3.dev.

# Press Machine v2.0

Windows OFX v2.0 release source. Hue Angle zero follows the existing skin chart reference; old red-zero variants remain separate. The release changes metadata only from the qualified SkinAxis trial; its binary has a separate limited Host receipt. See ../../docs/PressMachine-v2.0-Release.md for distribution, installation and known limits. The current DCTL test baseline stays available for use, investigation and implementation. No existing timeline or legacy OFX state is converted automatically.

All25 existing controls stay. Hue Angle zero has the intentional SkinAxis interpretation; other control meanings stay. OFX groups put color-space setup first, followed by Pre Saturation, Hue, Comp/Saturation Protection, Density and final desaturation. Hue Points offers1,2,3,4,6(default2). Density Bypass is a checkbox affecting Density only. Existing Skin Protect remains. Additional controls and expanded/new skin masks are deferred to v2.1.

## Source and build

Use one repository with shared math and separate DCTL/OFX adapters and releases. See ../../docs/PressMachine-v2-architecture.md. Immutable baseline1938 is at adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl. Shared math and pipeline are under core/press_machine/ in the repository root. regenerate.py emits the CPU/CUDA header and a separate development DCTL; its token test checks equality to the retained baseline except for the single approved active CF2 phase constant. Never overwrite the baseline with a generated artifact.

Validated build inputs: Windowsx64, Visual Studio2019 MSVC14.29, CMake4.4.3, Resolve21.1 build14's official OpenFX SDK, and its bundled NVRTC12.8. No new CUDA toolkit is installed. The NVIDIA driver must support the generated compute75 PTX and CUDA context IDs. The SDK itself is not included in this source package.

Run build.ps1 for generation, shader compile, CMake build, package-name/export checks and CPU checks. Add -Clean for a clean C++ rebuild. SDK path can be set with CMake RESOLVE_OFX_SDK. Output: build/PressMachineV2SkinAxis.ofx.bundle/Contents/Win64/PressMachineV2SkinAxis.ofx. 

Run tests/verify_cuda.py and tests/verify_cuda_adapter.py only when no Resolve playback or render benchmark is running. They create and release isolated CUDA contexts. The actual adapter harness verifies the same module loading/cache/stream code linked into the OFX, in addition to independent kernel parity.

## Rendering and limits

CPU and CUDA share the same pixel math. CUDA respects Host stream, image bounds, signed rowBytes and render window. Non-null Host stream rendering stays asynchronous; absent/default stream rendering completes before returning. Modules are keyed by unique context ID to avoid raw-pointer reuse. Ordinary renders have no image allocation, CPU readback or device-wide synchronization.

Alpha is copied. Premultiplied RGB uses correctly rounded component division, finite guards, and remultiplication. Unchanged colors retain the original premultiplied words. Zero-alpha hidden RGB is retained. Unrepresentable alpha conversion falls back to original RGBA rather than creating Inf/NaN. Opaque RGB is the DCTL equivalence contract.

Diagnostic revision 2 records CPU dispatch or successful CUDA enqueue through the non-popup OFX V1 MessageLog callback and local app-data PressMachine/OFXv2-test.log. KnownFolder resolves LocalAppData, with the environment value as fallback. Host messages include file stage, Win32 error code, KnownFolder HRESULT and path provider. Host log messages use a literal format string.

CPU and CUDA have separate success/retry state. A shared nonblocking sink gate defers contention without consuming retry budget or doing I/O. Each backend stops after successful delivery or three real failed attempts; completed/exhausted calls perform no formatting, path work or I/O. Exceptions in diagnostics do not escape into rendering. No controls, pixel math, kernel or PTX are changed by this diagnostic revision.

The build runs standalone diagnostic tests for retry/exception/concurrency behavior, blocked Host callback recovery, printf forwarding, file failure reporting and concurrent append/flush/close. Their files stay under an owned results fixture, not the user's live plugin log directory. Exclude startup logging and GPU module warm-up from steady-state timings. A CUDA enqueue trace is not itself proof of completed pixels or pixel equality.

Resolve Host load/UI, same-input operation, candidate-specific numeric output, persistence, real-footage/4K performance and broader visual acceptance must be reported separately. Do not transfer old DCTL/OFX results to a new binary. OpenCL/Metal, other OSes and Free/Studio cross-edition compatibility are not verified by this Windows candidate. There is no public installer or automatic legacy migration.

The bundle name and binary name must have the same stem: PressMachineV2SkinAxis.ofx.bundle/Contents/Win64/PressMachineV2SkinAxis.ofx. Package checks catch mismatches before installation. See the [OpenFX packaging specification](https://openfx.readthedocs.io/en/main/Reference/ofxPackaging.html).

## Skin-reference zero and compatibility

The reference is the existing Skin Protect chart swatch, D65 sRGB (194,150,130), transformed into the active CF2 linear BT.2020 chroma plane. Its phase is 0.72821991608931957 radians (41.723927749288961 degrees). The old zero is the BT.2020 red direction at 15.60296817142704 degrees. This is not a promise that every Oklab skin-mask center or a displayed vectorscope line shares one fixed CF2 angle.

The only creative-equation change is the pmcf_phase constant. Skin Protect masks, Points choices, other stages and all control ranges/defaults remain unchanged. Hue Angle zero is the intentional meaning change. Hue Compression zero is bit-identical to the retained baseline. One Point can still strongly tint neutrals or increase chroma; start at a moderate strength.

To retain a legacy physical target, newAngle = wrap360(oldAngle - 26.120959577861925). Old 30 maps to new 3.8790404221381; old 0/360 maps to new 333.8790404221381. Do not round converted values to the displayed slider increment. Binary32 conversion is not universally bit-identical, and independently wrapping animated keys may change interpolation. No node, preset or keyframe is migrated automatically.

This candidate has its own identifier com.46slv.PressMachine.v2.skinaxis, label Press Machine v2.0 and bundle PressMachineV2SkinAxis.ofx.bundle. Existing red-zero plugins and DCTL artifacts are retained. Its diagnostic lines include variant=SkinAxis, release=2.0.0 and the full plugin identifier to distinguish simultaneously loaded variants.

regenerate.py emits generated/PressMachine_Full_SkinAxis_TEST.dctl. A frozen candidate artifact, when included under adapters/dctl/candidates, must be checked against its recorded SHA256 and shared-core hash rather than edited directly.

## Limited Host acceptance for artifact50a9372f

The exact 50a9372f artifact passed Resolve21.1 build14 Windows load, 25-control UI, a skin-footage Angle0/Points1/Hue50 check, and variant-specific CUDA/Host-stream enqueue logging. Completed-frame OFX versus new native DCTL, and new native versus the legacy physical-angle reference, each had maximum error1.1920928955e-7 with no samples over the gate.

A normal restart preserved all25 displayed values, the image, five-node state and new PowerGrade; a fresh process emitted the SkinAxis trace. See results/HOST_LIMITED_ACCEPTANCE_SKINAXIS.json. This is one scene and one state, not broad visual qualification, automatic migration, clipping repair or a general performance result. The receipt applies only to its recorded artifact/core hashes.

## Release artifact14249fb9

The regular label is Press Machine v2.0; plugin identity and25 values remain stable. The exact release module passed its own normal-load/label, retained25-value/PowerGrade and release-specific CUDA Host-stream gate. Its one completed4096x2160 skin-scene frame is word-identical to predecessor50a: all35,389,440RGBA words match, RGB maximum absolute/normalized error0, finite with alpha1. See results/RELEASE_HOST_ACCEPTANCE.json. This metadata-only one-state/one-frame check does not expand the historical acceptance scope or establish sustained performance.
