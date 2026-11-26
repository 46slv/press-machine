# SatComp #19 — SC-03/04 and SC-09 checkpoint contract

Owner: Hermes Code `specialist-code`; same pinned candidate `769a014c22c5d857fd771a659672171340a753b1`. Existing Mission/Goal remains unchanged. No version upgrade, product package changes, external publication or vendor contact. Do not rerun the already closed normal defocus pair.

## SC-03/04: second-frame association and composition order

Use source index 1 only in the disposable SatComp project on Resolve `21.1.0.14` / Windows CUDA, matching native Full data, 640×360, 24 fps, RGB float (ZIP) RGBA. Off EXR must be byte-for-byte equal after decode, including alpha. For `straight`, `premult`, `linear_comp`, `log_comp_bad`, compare exact OLD and CANDIDATE active Linear settings, then candidate unchanged save/export/reopen. Score RGB absolute ≤ `2e-6`, alpha bit-exact; require a visible numeric effect on the qualified blended/opaque probe (≥`1e-3` rather than accepting bypass). Read back the selected file, all eight values, and Global Blend. Use the precomposed Linear/log control to tell whether the difference existed before the effect; do not call it a two-layer in-Resolve test. Measure association independently with noncommuting DWG→AP1/DI: straight, premult, declared alpha, matching reference and unchanged reopen. Record hidden RGB for A=0 separately from partial-alpha scoring. Do not confuse alpha retention with how RGB was associated.

The fixture hashes are in `reference-pack/manifest.json`; `measure_sc34.py` rechecks two independent EXR decoders and computes direct, relative-to-OFF, and association evidence. Closed once the qualified captures, positive/negative control, and persistence are read back and the test files recovered. Preserve failures and partial cases.

## SC-09: separate OpenFX host-path boundary

Standalone graphics kernel test is not Resolve acceptance. Build the uniquely named float RGBA CUDA-only filter `org.satcomp.diagnostic.opaquefloat8125.r1`, with no CPU fallback, returns `(8.125,8.125,0.375,1)` and does not read/blend input. Use exact prior OFF/direct/built-in full-wet fixture `goal-blend/satblend.000000.exr`. Attest real device writes on the two present NVIDIA GPUs; require scoped plugin registration via bundled Blackmagic OpenFX SDK README's Windows directory, fresh lease, only exact newly created module, one-node duplicate of OFF, same source/format. Compare immutable previous controls and new host output. Recover only the new module and return to safe scratch; no scope escalation if it cannot be unloaded safely. Output `8.125` everywhere while built-in retains R/G 0/16 supports route specificity, not general native-OFX correctness. Alpha=0 is excluded from this diagnosis.

## Product decision

The original interactive path is still RED even if this constant plug-in and direct Color both pass. Replacing it with a compiled OFX or a fixed direct LUT changes the delivery/interaction contract. Any product candidate under the original contract must first beat the HDR gate in the original ResolveFX route before spending effort on repeating the entire regression matrix. Separate unconfirmed items: real footage and practical visibility, other Resolve versions/GPU backends, alpha/chroma at conditions not covered here, and an actual fix retaining the exact eight controls on the same route.
