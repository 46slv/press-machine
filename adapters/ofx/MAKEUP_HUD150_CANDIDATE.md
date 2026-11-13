# Makeup Sat + HUD150 candidate (2026-11-12)

Approved conditioning order: raw Pre Sat -> raw Sat Comp -> raw Makeup Sat, followed by a single original-input Comp Skin mix. Hue -> Density -> Final follows. Makeup is appended as parameter 30, range 0..200, neutral 100, using the Pre model. Existing 29 IDs, indices, defaults and ranges remain stable; legacy native 29-value exports supply Makeup=100. CPU, generated DCTL and CUDA share the schema/core; regenerate PTX and OFX together (Parameters is now 120 bytes).

HUD: preserves variable swatches and previous automatic 1.5x four-panel placement. Hue neutral reference intentionally excludes conditioning/Makeup. Density graph uses the new core stages. Sat Comp HUD shows Pre/Makeup/Skin and explicitly labels its curve BASE COMP BEFORE MAKEUP, not a whole-block response.

Validation:
- Independent old native CPU comparison: 12,000 pixels / 48,000 RGBA words bit exact at Makeup100, including legacy 29-value exports.
- Makeup raw-chain/single-skin oracle: 165 cases; negative per-stage-protection fixture differs by 0.00218651.
- CPU/generated-DCTL CPU 75,877 checks; luma 14,535; CUDA kernel and adapter each 23,700 cases, max abs error 1.1920928955078125e-7; alpha 121 cases.
- HUD 12,130 checks; Density 5,434; neutral Hue 27,864 samples. Existing 1.5x placement preserved.
- Exact candidate OFX SHA256 fe11629a0280cb7fe33bcf980756d7f0349b01a750d4682d7775e2f6a99b03b5 loaded by Resolve in an independent imported old-29 QA project. Missing Makeup restored as100. Actual UI order and Graph values recognized; changed Pre120/Comp40/Makeup150 and Skin0/100.
- Real Resolve RGB FLOAT 800x1000 still exports: each of three states compared on 1,892 grid points to CPU, max error 5.960464477539063e-8. Not a full-image or all-profile proof.
- Makeup100 versus prior HUD150 old-29 Host export: entire scanline payload exact; only project camera UUID header differs.
- Active Makeup150 Graph ON/OFF: full EXR 9,616,590 bytes identical, SHA256 8fffa9d875cc35536bd67982f4206658c945f0ed12376115b39868f754ef8e63.
- Nonneutral Pre120/Comp40/Makeup150/Skin100 persisted across project save/load, checked in actual UI.
- Original installed OFX restored SHA256 1ba0c188abd7152894afe37f3549d741773ca8d793e2f3e87205120e7b9801c8. Original project settings and 14 jobs exact, original timeline restored, no render running. Candidate preserved outside plugin scan.

Limits: prototype, not formal release/user visual acceptance. Generated DCTL was CPU-compiled for parity, not evaluated as a Resolve DCTL effect. CUDA standalone tests do not prove this Host job used a CUDA callback. Host tests are one still/profile plus limited parameter states, not full product domain. Small viewport keeps existing fit cap/hide behavior rather than promising 1.5x below minimum. Exact build retains v3 ID/version3.1 for controlled QA; final distribution/version policy remains separate. Existing v2/main not modified.

## Additional bounded motion acceptance
SS-Note-ROG was offline at the live environment check and was not accessed; its candidate installation remains incomplete. On CDs, reused the official ARRI C046 AWG4/LogC4 source in a separately imported project, first clip only. Pre120/Comp40/Makeup150/CompSkin60, existing complementary Bias50/Split100/Pivot0/Width.25 Hue; Density/Final neutral. Candidate hash unchanged fe11629a.

One exact named job exported 206 unique frames / 8.583333s at 3840x2160 24fps H264 yuv420p, Complete100%, 17.2168s end-to-end, 130675818bytes. Independent ffprobe counted206 frames, and ffmpeg fully decoded with exit0 and no errors. Output SHA256 da84005553bb4b4635e6d88d0b09ec5604e62e5488b5ccbbba904c587e0e4fb7. Minimum disk free15,815,532,544bytes; 11GiB reserve guard never triggered.

This is a short all-conditioning-active actual motion export, not a timing comparison, realtime playback, long thermal/leak test, GPU callback attribution, pixel oracle or display colour acceptance. OutputSame LogC4 and lossy MP4 must not be presented as a Rec709 artistic deliverable. Only first clip was changed and included in the marked range; other repeated clips were not tested. Original OFX1ba0c188, original project settings/timeline and14jobs restored exactly after completion. A hidden-start UI was unavailable during preparation; no parameter or render claim was made until a normal visible restart and actual UI recipe confirmation. No crash was inferred from the missing window.
