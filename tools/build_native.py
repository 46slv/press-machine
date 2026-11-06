"""Build the actual DCTL with an existing C++ compiler; never installs tools."""
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT/'build'/('native.exe' if os.name == 'nt' else 'native')

def build(source="tests/native_harness.cpp", executable=None):
    executable = Path(executable) if executable else EXE
    executable.parent.mkdir(exist_ok=True)
    source = Path(source)
    relative_exe = executable.relative_to(ROOT).as_posix()
    compiler = os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++')
    identity = None
    if compiler:
        command = [compiler, '-std=c++17', '-O2', '-fno-fast-math',
                   '-ffp-contract=off', str(ROOT/source), '-o', str(executable)]
        identity = subprocess.run([compiler,'--version'],text=True,capture_output=True).stdout.splitlines()[0]
    elif os.name == 'nt':
        choices = []
        for base in ('ProgramFiles(x86)', 'ProgramFiles'):
            p = Path(os.environ.get(base, 'C:/Program Files'))/'Microsoft Visual Studio'
            choices.extend(p.glob('*/*/VC/Auxiliary/Build/vcvarsall.bat'))
        choices = sorted(p for p in choices if list((p.parents[2]/'Tools/MSVC').glob('*/bin/Hostx64/x64/cl.exe')))
        if not choices:
            raise RuntimeError('No existing native C++ compiler; installation is outside this task')
        vcvars = choices[-1]
        cl_path=sorted((vcvars.parents[2]/'Tools/MSVC').glob('*/bin/Hostx64/x64/cl.exe'))[-1]
        identity_run=subprocess.run([str(cl_path)],capture_output=True,text=True,errors='replace')
        identity=(identity_run.stderr+identity_run.stdout).splitlines()[0]
        # vcvars configures only this child process. All output remains in build/.
        # Pass a .cmd path to avoid Python list2cmdline escaping embedded quotes
        # for cmd.exe (which does not follow the C argv quote convention).
        script = ROOT/('build/compile.cmd' if executable == EXE else 'build/compile-domain.cmd')
        script.write_text(f'@call "{vcvars}" amd64 >nul\n'
                          '@if errorlevel 1 exit /b %errorlevel%\n'
                          '@cl /nologo /std:c++17 /O2 /fp:strict /EHsc /W4 '
                          f'/Fe:{relative_exe} /Fo:build/{executable.stem}.obj '
                          f'{source.as_posix()}\n', encoding='utf-8')
        command = ['cmd.exe', '/d', '/c', str(script.relative_to(ROOT))]
    else:
        raise RuntimeError('No existing C++ compiler; set CXX to an installed compiler')
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    log = run.stdout + run.stderr
    (ROOT/'build/compiler.txt').write_text(log, encoding='utf-8')
    print(log.strip())
    run.check_returncode()
    return {'command': command, 'compiler':identity,'compiler_output': log,
            'flags':'C++17 O2 strict IEEE floating point; no fast math, no contraction',
            'executable': relative_exe}

if __name__ == '__main__':
    build()
