param([switch]$Clean)
$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
try {
 python ..\vnext\regenerate.py
 python compile_cuda.py
 if($Clean -and (Test-Path build)){Remove-Item build -Recurse -Force}
 cmake -S . -B build -A x64
 cmake --build build --config Release
 $env:PM_VNEXT_NATIVE=(Resolve-Path 'build\Release\PressMachineVNextParity.dll')
 python tests\verify_cpu.py
 Write-Host 'vNext build + CPU focused checks PASS'
} finally { Pop-Location }
