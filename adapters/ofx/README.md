# Press Machine OFX v2.0 development

Equivalent-function Windows OFX migration from the retained19382145 DCTL. This is a TEST candidate, not a release or full product acceptance. The current DCTL test baseline stays available for use, investigation and implementation. No existing timeline or legacy OFX state is converted automatically.

All25 existing controls and their meanings stay. OFX groups put color-space setup first, followed by Pre Saturation, Hue, Comp/Saturation Protection, Density and final desaturation. Hue Points offers1,2,3,4,6(default2). Density Bypass is a checkbox affecting Density only. Existing Skin Protect remains. Additional controls and expanded/new skin masks are deferred to v2.1.

## Source and build

Use one repository with shared math and separate DCTL/OFX adapters and releases. See ../../docs/PressMachine-v2-architecture.md. Immutable baseline1938 is at adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl. Shared math and pipeline are under core/press_machine/ in the repository root. regenerate.py emits the CPU/CUDA header and a separate development DCTL; its token test checks mathematical equivalence to the retained baseline. Never overwrite the baseline with a generated artifact.

Validated build inputs: Windowsx64, Visual Studio2019 MSVC14.29, CMake4.4.3, Resolve21.1 build14's official OpenFX SDK, and its bundled NVRTC12.8. No new CUDA toolkit is installed. The NVIDIA driver must support the generated compute75 PTX and CUDA context IDs. The SDK itself is not included in this source package.

Run build.ps1 for generation, shader compile, CMake build and CPU checks. Add -Clean for a clean C++ rebuild. SDK path can be set with CMake RESOLVE_OFX_SDK. Output: build/PressMachineV2.ofx.bundle/Contents/Win64/PressMachine.ofx. 

Run tests/verify_cuda.py and tests/verify_cuda_adapter.py only when no Resolve playback or render benchmark is running. They create and release isolated CUDA contexts. The actual adapter harness verifies the same module loading/cache/stream code linked into the OFX, in addition to independent kernel parity.

## Rendering and limits

CPU and CUDA share the same pixel math. CUDA respects Host stream, image bounds, signed rowBytes and render window. Non-null Host stream rendering stays asynchronous; absent/default stream rendering completes before returning. Modules are keyed by unique context ID to avoid raw-pointer reuse. Ordinary renders have no image allocation, CPU readback or device-wide synchronization.

Alpha is copied. Premultiplied RGB uses correctly rounded component division, finite guards, and remultiplication. Unchanged colors retain the original premultiplied words. Zero-alpha hidden RGB is retained. Unrepresentable alpha conversion falls back to original RGBA rather than creating Inf/NaN. Opaque RGB is the DCTL equivalence contract.

A development log records the first actual CPU/CUDA render entry per process at the local app-data PressMachine/OFXv2-test.log. Exclude first-render logging and GPU module warm-up from steady-state timings. CUDA enqueue trace is not itself a pixel-correctness result.

Resolve Host load/UI, same-input operation, candidate-specific numeric output, persistence, real-footage/4K performance and broader visual acceptance must be reported separately. Do not transfer old DCTL/OFX results to a new binary. OpenCL/Metal, other OSes and Free/Studio cross-edition compatibility are not verified by this Windows candidate. There is no public installer or automatic legacy migration.
