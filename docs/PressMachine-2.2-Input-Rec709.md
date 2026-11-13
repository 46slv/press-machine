# Press Machine 2.2 input Rec.709 candidate

The owner's2026-11-13 input-gamut request is implemented as an append-only `Input Primaries: Rec.709 D65` choice (index4). It is primaries only. Input Transfer stays independent and unchanged; gamma2.4, sRGB and BT.709 OETF are NOT new supported transfer choices. For gamma-encoded709 material, match/linearize the actual signal upstream rather than pretending it is Relative Linear. Rec.709 D65 plus Relative Linear is appropriate only for actual scene-linear709 input. Output Same returns to709 using its inverse matrix. No new explicit output-primaries choice.

Existing input indices0..3, all transfer/output choices, parameter count30/defaults/IDs/order, plugin ID and four-panel Graph remain unchanged. Existing installed75799ec7 is not replaced automatically. A project saved using new input4 must not be overwritten with an older build lacking that choice.

## Focused evidence, not Host acceptance
- Native Windows OFX and compute75 PTX compile. Candidate binary SHA2567cec4092d3d35101fab71dab65f181d0aa382f7521906997a3d776be6db94876.
- Independent rational Rec.709/DWG chromaticity oracle:416 directional cases; max absolute matrix error2.984279490192421e-13.208 explicit matrix roundtrips.624 active Output-Same comparisons against independent conversion around the existing creative core, max2.226654075343504e-6 (fixed ordinary tolerance2^-13).
-1,040 neutral encoded bit-exact checks include out-of-domain transfer fallbacks: not a promise of valid-domain decoding for every supplied value.624 generated-DCTL-as-CPU exact cases.3,600 old-profile comparisons against the retained prior native DLL are word-exact; its hash is in REC709.json. Ordinary CI without that old DLL does not repeat this historical-binary comparison.
- Existing CPU/generated-DCTL profile wiring expanded to750 selector combinations. Existing Makeup165/NeutralHue27864/DensityGraph5434/HUD12130 and alpha121 focused checks pass. No artistic/operator change.
- Independent CUDA kernel and actual CudaRunner adapter each28,440 pixel cases across6 profile pairs including Rec.709/Relative Linear: maxCPU difference1.1920928955078125e-7. This is isolated-context parity, NOT actual Resolve job/backend/Host acceptance.

Exact-new-binary Resolve menu/parameter persistence/Graph/pixel testing and user delivery remain pending. No current installation, existing project, main/v2 or old trial was replaced by this source change. See the existing main specification's2026-11-13 amendment. Tests: verify_rec709.py, verify_vnext.py, verify_hud.py, verify_luma_curve.py, verify_cuda_v3.py and verify_cuda_adapter_v3.py.
