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
Measure-Step 'shared-source-generation' {python "$root\regenerate.py";python "$root\generate_descriptors.py"}
Measure-Step 'shader-NVRTC-compile' {python "$root\compile_cuda.py"}
Measure-Step 'CMake-configure' {cmake -S $root -B "$root\build" -G 'Visual Studio 16 2019' -A x64}
if($Clean){Measure-Step 'clean-generated-build' {cmake --build "$root\build" --config Release --target clean}}
Measure-Step 'CXX-compile-link' {cmake --build "$root\build" --config Release --parallel 4}
Measure-Step 'CPU-parity' {python "$root\tests\verify_cpu.py";python "$root\tests\verify_alpha.py"}
$records | ConvertTo-Json -Depth 5 | Set-Content "$root\results\BUILD_TIMINGS.json"
Get-FileHash -LiteralPath "$root\build\PressMachineV2.ofx.bundle\Contents\Win64\PressMachine.ofx" -Algorithm SHA256 | Format-List
# CUDA adapter/kernel tests use an isolated GPU context. Run only after
# coordinating with the sole Resolve Host benchmark owner:
# python "$root\tests\verify_cuda.py"
