param([switch]$Clean)
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$records=[Collections.Generic.List[object]]::new()
function Measure-Step([string]$Name,[scriptblock]$Action){
 $timer=[Diagnostics.Stopwatch]::StartNew()
 & $Action
 $code=$LASTEXITCODE
 $timer.Stop()
 $records.Add(@{step=$Name;seconds=$timer.Elapsed.TotalSeconds;exit_code=$code})
 if($code -ne 0){throw "$Name failed: $code"}
}
Measure-Step 'shared-source-generation' {python "$root\regenerate.py"}
Measure-Step 'UI-descriptor-generation' {python "$root\generate_descriptors.py"}
Measure-Step 'shader-NVRTC-compile' {python "$root\compile_cuda.py"}
Measure-Step 'CMake-configure' {cmake -S $root -B "$root\build" -G 'Visual Studio 16 2019' -A x64}
if($Clean){Measure-Step 'clean-generated-build' {cmake --build "$root\build" --config Release --target clean}}
Measure-Step 'CXX-compile-link' {cmake --build "$root\build" --config Release --parallel 4}
Measure-Step 'trace-logging-unit-tests' {& "$root\build\Release\PressMachineTraceTests.exe" "$root\results\trace-unit-fixture"}
New-Item -ItemType Directory -Force "$root\results\v3_curve\graph" | Out-Null
Measure-Step 'HUD-model-unit-tests' {& "$root\build\Release\PressMachineHudTests.exe" "$root\results\v3_curve\graph\HUD_MODEL.json"}
Measure-Step 'Density-interaction-focused-tests' {& "$root\build\Release\PressMachineDensityGraphTests.exe" "$root\results\v3_curve\graph\DENSITY_GRAPH.json"}
Measure-Step 'HUD-source-separation' {python "$root\tests\verify_hud_source.py"}
Measure-Step 'package-layout-and-exports' {python "$root\tests\verify_package_v3.py"}
Measure-Step 'vNext-focused-tests' {python "$root\tests\verify_vnext.py"}
Measure-Step 'CPU-alpha-extremes' {python "$root\tests\verify_alpha_v3.py"}
Measure-Step 'provisional-luma-curve' {python "$root\tests\verify_luma_curve.py"}
$records | ConvertTo-Json -Depth 5 | Set-Content "$root\results\v3_curve\BUILD_TIMINGS.json"
Get-FileHash -LiteralPath "$root\build\PressMachineV3CurveDev.ofx.bundle\Contents\Win64\PressMachineV3CurveDev.ofx" -Algorithm SHA256 | Format-List
# CUDA adapter/kernel tests use an isolated GPU context. Run only after
# coordinating with the sole Resolve Host benchmark owner:
# python "$root\tests\verify_cuda_v3.py"
