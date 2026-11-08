# Press Machine OFX v2.0 development

Equivalent-function Windows OFX migration from the retained19382145 DCTL. This is a TEST candidate, not a release or full product acceptance. The current DCTL test baseline stays available for use, investigation and implementation. No existing timeline or legacy OFX state is converted automatically.

All25 existing controls and their meanings stay. OFX groups put color-space setup first, followed by Pre Saturation, Hue, Comp/Saturation Protection, Density and final desaturation. Hue Points offers1,2,3,4,6(default2). Density Bypass is a checkbox affecting Density only. Existing Skin Protect remains. Additional controls and expanded/new skin masks are deferred to v2.1.

## Source and build

Use one repository with shared math and separate DCTL/OFX adapters and releases. See ../../docs/PressMachine-v2-architecture.md. Immutable baseline1938 is at adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl. Shared math and pipeline are under core/press_machine/ in the repository root. regenerate.py emits the CPU/CUDA header and a separate development DCTL; its token test checks mathematical equivalence to the retained baseline. Never overwrite the baseline with a generated artifact.

Validated build inputs: Windowsx64, Visual Studio2019 MSVC14.29, CMake4.4.3, Resolve21.1 build14's official OpenFX SDK, and its bundled NVRTC12.8. No new CUDA toolkit is installed. The NVIDIA driver must support the generated compute75 PTX and CUDA context IDs. The SDK itself is not included in this source package.

Run build.ps1 for generation, shader compile, CMake build, package-name/export checks and CPU checks. Add -Clean for a clean C++ rebuild. SDK path can be set with CMake RESOLVE_OFX_SDK. Output: build/PressMachineV2.ofx.bundle/Contents/Win64/PressMachineV2.ofx. 

Run tests/verify_cuda.py and tests/verify_cuda_adapter.py only when no Resolve playback or render benchmark is running. They create and release isolated CUDA contexts. The actual adapter harness verifies the same module loading/cache/stream code linked into the OFX, in addition to independent kernel parity.

## Rendering and limits

CPU and CUDA share the same pixel math. CUDA respects Host stream, image bounds, signed rowBytes and render window. Non-null Host stream rendering stays asynchronous; absent/default stream rendering completes before returning. Modules are keyed by unique context ID to avoid raw-pointer reuse. Ordinary renders have no image allocation, CPU readback or device-wide synchronization.

Alpha is copied. Premultiplied RGB uses correctly rounded component division, finite guards, and remultiplication. Unchanged colors retain the original premultiplied words. Zero-alpha hidden RGB is retained. Unrepresentable alpha conversion falls back to original RGBA rather than creating Inf/NaN. Opaque RGB is the DCTL equivalence contract.

Diagnostic revision 2 records CPU dispatch or successful CUDA enqueue through the non-popup OFX V1 MessageLog callback and local app-data PressMachine/OFXv2-test.log. KnownFolder resolves LocalAppData, with the environment value as fallback. Host messages include file stage, Win32 error code, KnownFolder HRESULT and path provider. Host log messages use a literal format string.

CPU and CUDA have separate success/retry state. A shared nonblocking sink gate defers contention without consuming retry budget or doing I/O. Each backend stops after successful delivery or three real failed attempts; completed/exhausted calls perform no formatting, path work or I/O. Exceptions in diagnostics do not escape into rendering. No controls, pixel math, kernel or PTX are changed by this diagnostic revision.

The build runs standalone diagnostic tests for retry/exception/concurrency behavior, blocked Host callback recovery, printf forwarding, file failure reporting and concurrent append/flush/close. Their files stay under an owned results fixture, not the user's live plugin log directory. Exclude startup logging and GPU module warm-up from steady-state timings. A CUDA enqueue trace is not itself proof of completed pixels or pixel equality.

Resolve Host load/UI, same-input operation, candidate-specific numeric output, persistence, real-footage/4K performance and broader visual acceptance must be reported separately. Do not transfer old DCTL/OFX results to a new binary. OpenCL/Metal, other OSes and Free/Studio cross-edition compatibility are not verified by this Windows candidate. There is no public installer or automatic legacy migration.

The bundle name and binary name must have the same stem: PressMachineV2.ofx.bundle/Contents/Win64/PressMachineV2.ofx. Package checks catch mismatches before installation. See the [OpenFX packaging specification](https://openfx.readthedocs.io/en/main/Reference/ofxPackaging.html).
