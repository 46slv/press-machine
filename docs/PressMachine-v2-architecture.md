# Press Machine v2.0 architecture

Use one repository, with separate adapters and releases. The same color transforms, pixel math, parameter meanings and numerical fixtures should not be maintained in two repositories: a fix could otherwise silently change only one backend.

Proposed final layout:
- core/: shared color/math and per-pixel pipeline, without UI or Host ownership.
- parameters/: stable IDs, types, ranges, defaults, menu index/value mappings and group order.
- adapters/dctl/: DCTL wrapper/generation and retained accepted artifacts.
- adapters/ofx/: OFX descriptor, render-window/stride/alpha adapter, CPU and CUDA execution.
- tests/: scalar reference, baseline parity, CPU/CUDA parity and candidate-specific Resolve receipts.
- docs/: design, limitations, acceptance and release notes.

This repository keeps DCTL and OFX adapters side by side. PixelMath.dctlh and PixelPipeline.dctlh are the shared math source; regenerate.py emits a CPU/CUDA header and a DCTL wrapper. The retained red-zero variant has exact math/pipeline token agreement with19382145; the SkinAxis trial permits only the one phase exception described below. The original byte-exact1938 artifact remains immutable at adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl. The generated DCTL is a new development artifact, not a replacement for the installed baseline.

Both variants keep all25 controls. SkinAxis intentionally changes Hue Angle zero; all other control meanings stay. The menu remains1,2,3,4,6(default2), Density Bypass is boolean and affects Density only. Inspector groups follow color-space setup then processing order. Existing Skin Protect stays; new controls, semantic/expanded skin masks and multi-image inputs wait for v2.1.

The OFX identifier is separate from legacy slots. No project/node/control state is automatically converted. In particular, old Points5 and fractional states remain on the old DCTL until a human chooses an allowed value. Replacing a DCTL node with OFX is a deliberate step, not an in-place upgrade.

CPU reads per-render immutable Parameters and processes only the render window. CUDA uses the same pixel source, Host-provided stream, image bounds and rowBytes. It has no ordinary-frame allocation, CPU readback or device-wide synchronization. Modules are cached per CUDA context; Windows uses the official installed NVIDIA driver. PTX is compiled ahead with Resolve's official bundled NVRTC12.8, embedded in the plugin and JITed by the driver. The build does not need a new toolkit install. No fast-math or implicit multiply-add contraction is enabled. Pair arithmetic preserves explicit rounding.

RGBA alpha is copied. Premultiplied nonzero-alpha RGB is evaluated straight then premultiplied again. Zero-alpha hidden RGB is retained. IsIdentity is conservative: same input/output profiles and every creative stage neutral. Output conversion is never skipped merely because creative controls are neutral.

Release DCTL and OFX separately, for example dctl/v1.x and ofx/v2.0.x. A shared commit/core hash links their provenance, while artifact SHA256 and backend-specific Host receipts prevent tests from being transferred incorrectly. Public binary release/installers, signing, macOS/Linux support and Resolve Free/Studio matrix are not implied by this Windows development build.

## Separate SkinAxis trial

The SkinAxis TEST candidate changes only the active CF2 phase constant to the existing D65 sRGB skin chart direction. Its token gate reverses precisely that one approved function before comparing all remaining math/pipeline tokens to19382145. It uses a distinct plugin identifier and bundle, preserving red-zero artifacts and project behavior.

Tests distinguish exact agreement with a phase-adjusted1938 equation reference, Hue-off exact agreement with original1938, an independent chart-axis equation check, and tolerance-based legacy angle translation. Legacy translation is not automatic or universally bit-identical. Additional mask controls remain outside this change.
