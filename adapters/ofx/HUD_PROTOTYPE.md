# Read-only core-linked HUD prototype

This branch is an isolated development candidate. It is not a release and has not yet passed Resolve viewer/export acceptance.

- Plugin label: **Press Machine v2 SkinAxis HUD TEST**
- Plugin ID: **com.46slv.PressMachine.v2.skinaxis.hud**
- Bundle/binary stem: **PressMachineV2SkinAxisHUD**
- Trace: **variant=SkinAxisHUD**, %LOCALAPPDATA%/PressMachine/OFXv2-hud-test.log
- Qualified processing-code base: 02c57f0e93ae27b25b97ab6f1b5e1a51c8da2235
- New control: **Graph**, default off. One display switch only; no HUD editing, dragging, resizing or individual-panel controls.
- Processing: the same 25-parameter SkinAxis core. Graph is not passed to render, identity, the CPU pixel function or CUDA.

## Four panels

These are current parameter values and sampled processing laws, not measurements of the footage or a histogram.

1. **Hue**: current Angle, Points and Hue Compression; one maximum-saturation display swatch per target direction. Directions use the core's CF2 skin-reference phase. Angle zero is the existing D65 sRGB (194,150,130) chart reference in that plane, not every person's skin or an exact vectorscope line. Swatches map that direction to the sRGB boundary for a direction key; they do not predict final RGB. N=1 is one direction, N=2 a signed axis, N=3/4/6 equally spaced directions.
2. **Compression**: S input/output from 0 to 100, where S=100*C/abs(L) in the core's unprotected base saturation law. Calls the real UI threshold mapping, raw-threshold conversion and paired continuous-scale function. Threshold 100 and Amount 0 bypass exactly. The Skin value is shown; actual pixels can be protected differently and negative/proxy paths are not represented by a single universal line.
3. **Density**: actual Density, Chroma, Response, Shadow Protect/Range, Highlight Protect/Range, Skin Protect and active/bypass state. Values are UI settings, not stops. Bypass applies to Density only. No fabricated universal density curve or image measurement.
4. **Final Sat Keep**: remaining saturation 0-100% against DI(Y) 0-1. Uses the product of both shared keep functions, including overlap and zero-knee steps. The horizontal axis is not IRE. Values above 1 are outside this small plot. Core nonpositive-Y policy remains unchanged.

The shared protection masks are calculated from the original input by the processing core, not from the HUD or a frame readback.

## Implementation

- Standard OFX V1 viewer overlay, OpenGL compatibility drawing, read-only pen/key defaults.
- Resolve's bundled SDK setter registers V2/DrawSuite, so this branch explicitly registers the V1 entry property without changing the SDK.
- Panels fit the visible image/viewport intersection, four corners. Source RoD is projected through the host's original matrices. Small viewports suppress the HUD rather than cover the frame.
- No image fetch, GPU readback/context creation, framebuffer clear, swap, parameter write or persistent GL resource in the overlay.
- Original GL attribute state, matrix stacks and matrix mode are restored.
- All 25 parameter handles and Graph are redraw dependencies. Parameters are read at the host draw time; the display model is cached until values change.
- Graph is nonanimated with EvaluateOnChange=false. That is a host hint, not a guarantee against unnecessary host re-evaluation.
- Actual viewer appearance requires host overlay support and the OpenFX overlay mode for the selected effect. Host playback/UI-overlay preferences may hide it. A checkbox cannot force the host to call an overlay.

## Offline validation

Run adapters/ofx/build.ps1 -Clean. It regenerates shared code/descriptors/PTX, builds the plugin and tests, then runs source separation, package exports, CPU parity, SkinAxis and alpha tests. NVRTC compilation does not launch a GPU context. GPU tests are deliberately separate and must be coordinated with the sole Host owner.

results/HUD_SOURCE_SEPARATION.json proves all core files, processing schema, CUDA runner/kernel and native reference are unchanged from the qualified base. Both full Processor and PressMachine class bodies are exact. Graph appears only in the OFX descriptor/overlay, not the generated processing code.

results/HUD_MODEL.json covers the scalar compression oracle, threshold bypass, all Point counts, 0/360 equality, finite maximum-saturation swatches, final overlap/step boundaries, and 1,000 model-before/after pixel byte comparisons. Its mean model rebuild time is CPU-only, not a viewer FPS measurement.

An independent read-only review found no blocking delta defect. Actual host callback GL state, display redraw and export non-burn-in remain host acceptance items.

Inherited CUDA result files explicitly identify the old qualified SkinAxis base. They are not HUD-candidate GPU evidence.

## Required Resolve acceptance, owned by the sole Host operator

Do not install or touch an existing bundle/cache/project from this workspace. Preserve the current project and confirm no render is running before any agreed restart.

1. Install only the isolated HUD bundle under its distinct stem/ID; verify all old SkinAxis/red-zero plugins remain untouched.
2. In a new or preserved scratch project, add the HUD effect, select its node, enable the host's OpenFX overlay mode.
3. Graph off: no panels. Graph on: four small panels over the image. Toggle repeatedly. Confirm the inspector switch alone controls visibility.
4. Change Angle (including 0/360), all five Points options, Amount/Knee/Threshold (especially Threshold 100), Density Bypass and final zero-knee/overlap cases. Confirm panels update without any HUD interactions.
5. Compare identical lossless/float outputs with Graph off/on at the same parameter/time state; require pixel/alpha equality. An overlay-only implementation must not burn into exports. Record actual export evidence rather than infer acceptance from CPU tests.
6. Check paused/playback visibility, selected/unselected effect, host overlays off/on, fit/zoom/pan, viewer resize, proxy/render scales and applicable HiDPI/PAR cases. Record host-dependent limits rather than silently changing the design.
7. Confirm CPU/CUDA backend trace belongs to the HUD ID/tag, and playback performance is not materially degraded. Independent GPU tests require a separately agreed slot.

Until those tests pass, this is an offline-validated prototype, not a host-qualified trial release.
