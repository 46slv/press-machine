# Read-only Density-response HUD candidate

This branch is an isolated development candidate. It is not a release and has not yet passed Resolve viewer/export acceptance.

- Plugin label: **Press Machine v2 Density HUD TEST**
- Plugin ID: **com.46slv.PressMachine.v2.skinaxis.hud.density**
- Bundle/binary stem: **PressMachineV2SkinAxisHUDDensity**
- Trace: **variant=SkinAxisHUDDensity**, %LOCALAPPDATA%/PressMachine/OFXv2-hud-density-test.log
- Qualified processing-code base: 02c57f0e93ae27b25b97ab6f1b5e1a51c8da2235
- New control: **Graph**, default off. One display switch only; no HUD editing, dragging, resizing or individual-panel controls.
- Processing: the same 25-parameter SkinAxis core. Graph is not passed to render, identity, the CPU pixel function or CUDA.

## Four panels

These are current parameter values and sampled processing laws, not measurements of the footage or a histogram.

1. **Hue**: current Angle, Points and Hue Compression; one maximum-saturation display swatch per target direction. Directions use the core's CF2 skin-reference phase. Angle zero is the existing D65 sRGB (194,150,130) chart reference in that plane, not every person's skin or an exact vectorscope line. Swatches map that direction to the sRGB boundary for a direction key; they do not predict final RGB. N=1 is one direction, N=2 a signed axis, N=3/4/6 equally spaced directions.
2. **Compression**: S input/output from 0 to 100, where S=100*C/abs(L) in the core's unprotected base saturation law. Calls the real UI threshold mapping, raw-threshold conversion and paired continuous-scale function. Threshold 100 and Amount 0 bypass exactly. The Skin value is shown; actual pixels can be protected differently and negative/proxy paths are not represented by a single universal line.
3. **Density**: two actual-core response plots for fixed Skin/Red/Blue reference colors. Upper Delta EV is log2(Ydensity/Ycomp), lower Delta S percent is 100*((C/L)density/(C/L)comp-1), with Oklab S=C/L. X is original reference-input EV: each probe is normalized to Y=.18 at 0 EV and swept from -6 to +6. This is Comp-to-Density only, not the final image or a footage measurement. Original-input Skin masks and current Pre/Hue/Comp settings are retained. Final Desat and input/output encoding settings are outside this measurement. Near-neutral Comp denominators produce gaps, not false zeroes. Axes show their current plus/minus ranges; labels expand in engineering notation rather than silently clipping. D/C/R values remain above the graph; DENSITY OFF means Bypass. This one panel is 14 base pixels taller to keep its scope readable.
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

## Density parameter interactions and representative limits

The three fixed nonlinear D65 sRGB reference definitions are Skin=(194,150,130)/255, Red=(.80,.15,.10), Blue=(.12,.25,.85). They are decoded, converted to linear DWG, then normalized by actual Y before exposure scaling. They are not the current image colors or the Hue selector's swatches.

- Density controls the sign/strength of Delta EV. At zero, Density and Chroma effects are both zero.
- Chroma changes lower Delta S percent while upper Delta EV remains unchanged by the core's Y correction. It is not an independent effect when Density is zero.
- Response changes the saturation-dependent weighting of both effects; color probes can respond differently.
- Shadow Protect/Range changes the low-exposure part. Range alone does nothing if Protect is zero.
- Highlight Protect/Range changes the high-exposure part. Range alone does nothing if Protect is zero.
- Density Skin Protect changes the Skin-reference response more than Blue. It is not a universal all-skin detector; reference probes do not cover every hue, gamut boundary, negative RGB or subject.
- Bypass flattens both plots regardless of the retained settings.
- Pre/Hue/Compression can change the Density response because the same original probes pass through them first. The Skin mask is still calculated from the original input.
- Curves can coincide, be flat, or have omitted relative-saturation sections. Those are valid results, not permission to fabricate visible movement.

DENSITY_GRAPH.json records focused invariants, required valid-sample counts, range-label width and a deliberately nonzero-Chroma/strong-Density/upstream-enabled benchmark. The reported assertion count includes repeated per-sample range assertions, not thousands of independent scenarios.

Both plots share 99 stage evaluations per model rebuild. Rebuilding occurs when parameter values change, not on every unchanged draw; animation or dragging can incur this cost each draw. CPU timings do not qualify playback FPS. No pixel readback, live image scan or GPU context is added.

### Additional Host gate

Use only this candidate's distinct bundle/ID; preserve the accepted ca6 HUD and official release. Check all Hue Points options 1,2,3,4,6 (5 remains intentionally absent), and focused Density/Chroma/Response/Shadow+Range/Highlight+Range/Skin/Bypass interactions. Compare Graph on/off raw output exactly, then check repeated draw and short playback. Record probe limits and any unmeasured long-video/HiDPI/PAR/proxy/viewport conditions.
