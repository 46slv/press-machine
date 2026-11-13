$ErrorActionPreference='Stop'
. "$PSScriptRoot/../SelectBuildGenerator.ps1"
$r=Join-Path $env:TEMP ('pm-generator-'+[guid]::NewGuid());New-Item -ItemType Directory "$r/build"|Out-Null
function Require($x){if(-not $x){throw 'test failed'}}
function Reject([scriptblock]$f){$rejected=$false;try{&$f|Out-Null}catch{$rejected=$true};Require $rejected}
$a=Get-PressMachineConfigureArguments $r '' '';Require (-not($a -contains '-G'));Require ($a[-1] -eq 'x64')
$a=Get-PressMachineConfigureArguments $r 'Visual Studio 16 2019' '';Require ($a -contains 'Visual Studio 16 2019')
$a=Get-PressMachineConfigureArguments $r '' 'Visual Studio 17 2022';Require ($a -contains 'Visual Studio 17 2022')
Reject {Get-PressMachineConfigureArguments $r 'Ninja' ''}
@('CMAKE_GENERATOR:INTERNAL=Visual Studio 17 2022','CMAKE_GENERATOR_PLATFORM:INTERNAL=x64')|Set-Content "$r/build/CMakeCache.txt"
$before=(Get-FileHash "$r/build/CMakeCache.txt").Hash
$a=Get-PressMachineConfigureArguments $r '' '';Require ($a -contains 'Visual Studio 17 2022')
Reject {Get-PressMachineConfigureArguments $r 'Visual Studio 16 2019' ''}
Reject {Get-PressMachineConfigureArguments $r '' 'Visual Studio 16 2019'}
Require ((Get-FileHash "$r/build/CMakeCache.txt").Hash -eq $before)
@('CMAKE_GENERATOR:INTERNAL=Visual Studio 17 2022','CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32')|Set-Content "$r/build/CMakeCache.txt"
Reject {Get-PressMachineConfigureArguments $r '' ''}
Write-Output 'PASS: default, explicit2019, environment2022, cache2022, unsupported, explicit/environment conflicts, x86 rejection, cache unchanged'
