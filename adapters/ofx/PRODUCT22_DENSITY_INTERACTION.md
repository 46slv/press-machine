# Press Machine 2.2 Density interaction: bounded DCTL Host evidence

This record contains test settings, numerical results and hashes only. No photograph, video, rendered image, project, private path or credentials are included.

## Conditions
Actual Resolve built-in DCTL using the current2.2 shared core. Exact DCTL SHA256 ae50fc47726103e12041186a287c4f3ef0580c3074092c86993ecae7942121ca. RGB FLOAT800x1000, opaque DWG/DaVinci Intermediate input, outputSame, one still. This is not an OFX Host test or a generated-DCTL-as-CPU test.

Common settings: Pre120,Threshold80,Comp40,Knee20,Makeup150,CompSkin50; Complementary,Angle45,Strength50,Bias-25,Split100,Pivot0,Width1; DensityChroma0,Response2,tone protections0,Final neutral. Existing D0/LookSkin0 output was reused, not rendered again. Only D100/LookSkin0 and D100/LookSkin60 were added.

Each new state:1892 fixed grid pixels versus current native CPU core, maximum absolute RGB difference5.960464477539063e-8, threshold2^-13, all outputRGB finite. Exact30 settings and output hashes are in results/v3_curve/PRODUCT22_DENSITY_DCTL_HOST.json.

- D100/Look0 output SHA256 a119482739e5723d16ce98ad922ed0f2aec9954e37328c963ef89755c405f7c9.
- D100/Look60 output SHA256 ab6cdd672cad4b7503d1f20916c37cdb6333da4825347caf2c3f48fb69daf3a8.
- Reused D0/Look0 output SHA256 cc3a7f4326bd2660d55aee3e198db3cb98ab9d69555186b7bb3eb8a5543e551f.

## Interpretation limits
Look Skin protects the combined Hue+Density net change, not Density alone; these states do not isolate a Density-only skin mask. One still/profile, sampled active parity, no alpha or full-pixel active oracle, motion, wide-range, perceptual or whole-product acceptance claim. No new Hue operator, Density formula, white-fringe correction or research texture model was adopted. Existing labT is not productionDensity and was not incorporated. This is baseline integration evidence, not a declaration that all nonDensity acceptance is complete.
