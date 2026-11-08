import ctypes as c,json,time,hashlib,os
from pathlib import Path
r=Path(__file__).resolve().parent
dll=Path(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\nvrtc64_120_0.dll')
dll_directory=os.add_dll_directory(str(dll.parent))
builtins=c.WinDLL(str(dll.parent/"nvrtc-builtins64_128.dll"))
lib=c.WinDLL(str(dll))
lib.nvrtcCreateProgram.argtypes=[c.POINTER(c.c_void_p),c.c_char_p,c.c_char_p,c.c_int,c.POINTER(c.c_char_p),c.POINTER(c.c_char_p)]
lib.nvrtcCompileProgram.argtypes=[c.c_void_p,c.c_int,c.POINTER(c.c_char_p)]
lib.nvrtcGetProgramLogSize.argtypes=[c.c_void_p,c.POINTER(c.c_size_t)]
lib.nvrtcGetProgramLog.argtypes=[c.c_void_p,c.c_void_p]
lib.nvrtcGetPTXSize.argtypes=[c.c_void_p,c.POINTER(c.c_size_t)]
lib.nvrtcGetPTX.argtypes=[c.c_void_p,c.c_void_p]
lib.nvrtcDestroyProgram.argtypes=[c.POINTER(c.c_void_p)]
source=(r/'src/Kernel.cu').read_text().replace('#include "../generated/PixelCore.hpp"',(r/'generated/PixelCore.hpp').read_text())
options=[b'--gpu-architecture=compute_75',b'--std=c++14',b'--fmad=false',b'--prec-div=true',b'--prec-sqrt=true',b'--ftz=false']
program=c.c_void_p()
assert lib.nvrtcCreateProgram(c.byref(program),source.encode(),b'PressMachineKernel.cu',0,None,None)==0
start=time.perf_counter();status=lib.nvrtcCompileProgram(program,len(options),(c.c_char_p*len(options))(*options));elapsed=time.perf_counter()-start
size=c.c_size_t();lib.nvrtcGetProgramLogSize(program,c.byref(size));buf=c.create_string_buffer(size.value);lib.nvrtcGetProgramLog(program,buf)
log=buf.value.decode(errors='replace');(r/'results/NVRTC.log').write_text(log)
receipt=dict(status=status,seconds=elapsed,compiler=str(dll),options=[x.decode() for x in options],source_sha256=hashlib.sha256(source.encode()).hexdigest())
if status==0:
 lib.nvrtcGetPTXSize(program,c.byref(size));buf=c.create_string_buffer(size.value);assert lib.nvrtcGetPTX(program,buf)==0
 ptx=buf.value;(r/'generated/Kernel.ptx').write_bytes(ptx);receipt.update(ptx_sha256=hashlib.sha256(ptx).hexdigest(),ptx_bytes=len(ptx))
 (r/'generated/KernelPtx.hpp').write_text('#pragma once\nstatic const char kPressMachinePtx[] = R"PMPTX('+ptx.decode()+')PMPTX";\n')
lib.nvrtcDestroyProgram(c.byref(program))
(r/'results/NVRTC.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));print(log[-5000:])
raise SystemExit(status)
