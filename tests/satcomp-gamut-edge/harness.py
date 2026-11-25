import ctypes as C
import hashlib
import os
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'fixtures/PressMachine_Comp_Color_Normalized_TEST.dctl'
CAND=ROOT.parents[1]/'adapters/dctl/candidates/PressMachine_Comp_Color_Normalized_GamutEdge_20261125.dctl'
PIN='db784f2fd24c7e34df9a33f56e1f93ba202df3fccbd924c17a0c92f5b092bb75'
if hashlib.sha256(BASE.read_bytes()).hexdigest() != PIN: raise ValueError("Wrong baseline fixture bytes")
OUT=Path(os.environ["SATCOMP_REPLAY_OUT"])
if sys.platform=='win32':
    mingw=os.add_dll_directory(os.environ['SATCOMP_REPLAY_DLL_DIR'])

def bits(x): return struct.pack('<f',x)
def f32(x): return C.c_float(float(x)).value
def same(a,b): return all(bits(x)==bits(y) for x,y in zip(a,b))
def maxerr(a,b): return max(abs(float(x)-float(y)) for x,y in zip(a,b))
def inp32(rgb): return tuple(map(f32,rgb))

def load(lane):
    lib=C.CDLL(str(OUT/f'{lane}.dll'))
    entry=lib.cpu_transform
    entry.restype=None
    entry.argtypes=(C.POINTER(C.c_float),C.POINTER(C.c_float),C.POINTER(C.c_int),C.POINTER(C.c_float))
    def run(rgb,*,ig=0,it=4,og=None,ot=None,threshold=25,amount=0,knee=20,bypass=0,xy=(1,1,0,0)):
        inp=(C.c_float*3)(*rgb); out=(C.c_float*3)()
        slider=(C.c_float*3)(threshold,amount,knee)
        controls=(C.c_int*9)(bypass,ig,it,0 if og is None else og+1,0 if ot is None else ot+1,*xy)
        entry(inp,slider,controls,out)
        return tuple(out)
    return run
