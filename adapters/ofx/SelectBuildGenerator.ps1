function Get-PressMachineConfigureArguments {
 param([string]$Root,[string]$Generator='', [string]$EnvironmentGenerator=$env:CMAKE_GENERATOR)
 $cache=Join-Path $Root 'build/CMakeCache.txt'
 $cached='';$platform=''
 if(Test-Path -LiteralPath $cache){
  foreach($line in Get-Content -LiteralPath $cache){
   if($line -match '^CMAKE_GENERATOR:INTERNAL=(.*)$'){$cached=$Matches[1]}
   if($line -match '^CMAKE_GENERATOR_PLATFORM:INTERNAL=(.*)$'){$platform=$Matches[1]}
  }
 }
 $selected=$Generator
 if(-not $selected){$selected=$cached}
 if(-not $selected){$selected=$EnvironmentGenerator}
 if($cached -and $Generator -and $cached -ne $Generator){throw 'Explicit generator conflicts with existing cache; use a separate build directory.'}
 if($cached -and -not $Generator -and $EnvironmentGenerator -and $cached -ne $EnvironmentGenerator){throw 'Environment generator conflicts with existing cache.'}
 if($selected -and $selected -notmatch '^Visual Studio [0-9]+ [0-9]{4}$'){throw 'Only Visual Studio generators are supported by this Windows build.'}
 if($platform -and $platform -ne 'x64'){throw 'Existing cache platform is not x64.'}
 $arguments=@('-S',$Root,'-B',(Join-Path $Root 'build'))
 if($selected){$arguments+=@('-G',$selected)}
 $arguments+=@('-A','x64')
 return $arguments
}
