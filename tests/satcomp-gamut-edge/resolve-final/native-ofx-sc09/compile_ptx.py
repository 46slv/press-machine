"""Compile the diagnostic kernel with the workstation's existing bundled NVRTC."""
import ctypes as C
import hashlib,json,os
from pathlib import Path
p=Path(__file__).resolve().parent
win=Path('C:/Program Files/Blackmagic Design/DaVinci Resolve')
directory=os.add_dll_directory(str(win)); builtins=C.WinDLL(str(win/'nvrtc-builtins64_128.dll'))
f=C.WinDLL(str(win/'nvrtc64_120_0.dll')); V=C.c_void_p; I=C.c_int; Z=C.c_size_t; P=C.c_char_p
for name,types in {'CreateProgram':[C.POINTER(V),P,P,I,C.POINTER(P),C.POINTER(P)],'CompileProgram':[V,I,C.POINTER(P)],'GetProgramLogSize':[V,C.POINTER(Z)],'GetProgramLog':[V,V],'GetPTXSize':[V,C.POINTER(Z)],'GetPTX':[V,V],'DestroyProgram':[C.POINTER(V)]}.items(): getattr(f,'nvrtc'+name).argtypes=types
src=(p/'constant.cu').read_bytes(); prog=V(); opts=[b'--gpu-architecture=compute_75',b'--std=c++14',b'--fmad=false']; h=lambda x:hashlib.sha256(x).hexdigest()
def ck(q):
    if q: raise RuntimeError('NVRTC error '+str(q))
ck(f.nvrtcCreateProgram(C.byref(prog),src,b'constant.cu',0,None,None))
try:
    result=f.nvrtcCompileProgram(prog,len(opts),(P*len(opts))(*opts)); n=Z(); ck(f.nvrtcGetProgramLogSize(prog,C.byref(n))); buf=C.create_string_buffer(n.value); ck(f.nvrtcGetProgramLog(prog,buf))
    if result: raise RuntimeError(buf.value.decode(errors='replace'))
    ck(f.nvrtcGetPTXSize(prog,C.byref(n))); buf=C.create_string_buffer(n.value); ck(f.nvrtcGetPTX(prog,buf)); ptx=buf.value
    assert b'.entry sat19_opaque_8125' in ptx
    generated=b'#pragma once\nconstexpr char kPtx[] = R"SAT19PTX('+ptx+b')SAT19PTX";\n'
    with (p/'constant_ptx.hpp').open('xb') as o:o.write(generated)
    print(json.dumps({'kernel_sha256':h(src),'ptx_sha256':h(ptx),'header_sha256':h(generated),'compute':'75','nvrtc_log':buf.value[:0].decode()},indent=2))
finally: ck(f.nvrtcDestroyProgram(C.byref(prog)))
