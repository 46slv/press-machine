# Handoff for subsequent Resolve validation

This task performed no Resolve/GUI operation and staged no DCTL. Freshly verify
host/project/render/save state, exact current writer and installed hashes before
any later host operation. Existing projects/media must be preserved.

## Artifacts, do not conflate them

- Baseline R2 37e0c2e: source archive in
  D:/Documents/Codex/PressMachine-AR3-20261107, SHA256 1a679a3a8fd4a3cca5d93a1fd61f995ed44d6befa3b2aa4fc1e188aaa9eea438.
- `dctl/PressMachine_R2.dctl`: same R2 domain/controls, scalar precision repair,
  SHA256 b703789d8346a44ed6139cc66835d6a38e0affd96287e2ea043532b14abe1e55.
- `prototypes/PressMachine_ContinuousDomain.dctl`: isolated signed-L domain
  revision proposal, SHA256 f019e39ed6e5b928c2f05acb5c2586ff82527dcad66bc9112e0c41465da1d401.
  Do not replace the approved R2 artifact/brief with this without a decision.

Use unique staging names, archive/read back exact hashes and remove only the
owned staged files after tests. Do not overwrite A2 or any other installation.

## Bounded validation sequence, after the relevant approval

1. ValidateDCTL/parser/load/actual GPU execution of the chosen source. The new
   scalar helpers use SDK float2/make_float2/_fmaf. Native C++ is not proof that
   Resolve's compiler preserves the compensated calculations.
2. Use the owned scratch project PressMachine_AR3_CST_20261107_0420 and saved
   scratch-synthetic-chart.drp only after fresh inspection, if still suitable.
   Chain: DWG/Linear -> DWG/DI (mapping None) -> chosen DCTL -> DWG/Linear
   (mapping None). Do not repeat old C0/Bypass work unchanged; a changed artifact
   needs targeted regression. Capture exact node/UI/export settings.
3. Compare T25/P20 C75 on the exact synthetic blue chart. Examine peak-1
   x2737->2738 and the separate LMS-zero steep slope near x2620->2621 (local
   572->573). Compare exact source/oracle/captured buffers. R2 scalar repair
   intentionally does not fix the L-guard jump; only the approved revised-domain
   artifact should be judged against that proposal's expected result.
4. Repeat matched Bypass/C50/C100 stills using the existing skin and highlight
   source files. Use their prior Rec.709/Linear interpretation only with its
   documented metadata limitation. Inspect the dark/noise and negative-value
   affected pixels, not just overall appearance. No new broad acquisition is
   needed for this bounded comparison.
5. Validate finite negative/>1, signed L/hue/chroma behavior and targeted
   relative identity/alpha. Existing absolute signed-zero issue is separate.
   For strict float alpha export, prior evidence established Individual Clips,
   actual Straight selected, full levels, EXR float. API AlphaMode alone was not
   reliable in Single Clip mode. Read back sample values as well as settings.
6. Measure runtime cost with alternating same-timeline baseline/processed
   controls, warmup and equivalent cache/proxy/render settings. Record dropped
   frames/control responsiveness if judging playback. CPU microbenchmark is
   not a substitute. Make a matched visual comparison for the remaining steep
   LMS-zero slope before calling the proposal usable.
7. Preserve source commit, hashes, Resolve build/backend/GPU, settings, numeric
   results, matched stills and limitations. Save/export owned scratch, check no
   active renders, remove only verified task staging and release writer.

Product acceptance and user's visual judgment remain open. No push, merge,
release, install, production deployment or Notion-contract change is implied.
