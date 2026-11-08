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
Measure-Step 'HUD-model-unit-tests' {& "$root\build\Release\PressMachineHudTests.exe" "$root\results\HUD_MODEL.json"}
Measure-Step 'HUD-source-separation' {python "$root\tests\verify_hud_source.py"}
Measure-Step 'package-layout-and-exports' {python "$root\tests\verify_package.py"}
Measure-Step 'CPU-parity' {python "$root\tests\verify_cpu.py"}
Measure-Step 'skin-axis-phase-and-legacy' {python "$root\tests\verify_skin_axis.py"}
Measure-Step 'CPU-alpha-extremes' {python "$root\tests\verify_alpha.py"}
$records | ConvertTo-Json -Depth 5 | Set-Content "$root\results\BUILD_TIMINGS.json"
Get-FileHash -LiteralPath "$root\build\PressMachineV2SkinAxisHUD.ofx.bundle\Contents\Win64\PressMachineV2SkinAxisHUD.ofx" -Algorithm SHA256 | Format-List
# CUDA adapter/kernel tests use an isolated GPU context. Run only after
# coordinating with the sole Resolve Host benchmark owner:
# python "$root\tests\verify_cuda.py"
