"""Run the pinned SC09 constant kernel on each actual local CUDA device, not in Resolve."""
import ctypes as C
import hashlib,json,struct
from pathlib import Path
B=Path(__file__).resolve().parent/'build'; H=B/'Release/SatCompSC09Harness.dll'; P=B/'SatCompSC09Opaque.ofx.bundle/Contents/Win64/SatCompSC09Opaque.ofx'
V=C.c_void_p; U=C.c_uint; I=C.c_int; L=C.c_ulonglong; Z=C.c_size_t
class Plugin(C.Structure):
    _fields_=[('api',C.c_char_p),('abi',I),('id',C.c_char_p),('major',U),('minor',U),('setHost',V),('entry',V)]

def bind(l,n,*t):
    f=getattr(l,n); f.argtypes=list(t); f.restype=I; return f

def check(r):
    if r: raise RuntimeError(f'CUDA status {r}')

c=C.WinDLL('C:/Windows/System32/nvcuda.dll'); plug=C.CDLL(str(P)); test=C.CDLL(str(H)); count=I()
ids=[]
for lib in (plug,test):
    get=lib.OfxGetPlugin; get.argtypes=[I]; get.restype=C.POINTER(Plugin)
    assert lib.OfxGetNumberOfPlugins()==1 and not get(-1) and not get(1)
    p=get(0).contents; assert p.api==b'OfxImageEffectPluginAPI' and p.id==b'org.satcomp.diagnostic.opaquefloat8125.r1' and (p.abi,p.major,p.minor)==(1,1,0) and p.entry and p.setHost
    ids.append(p.id.decode())
assert not hasattr(plug,'Sat19TestGpuFill')
fill=bind(test,'Sat19TestGpuFill',V,C.c_longlong,I,I,I,I)
check(bind(c,'cuInit',U)(0)); check(bind(c,'cuDeviceGetCount',C.POINTER(I))(C.byref(count)))
assert count.value>=1
w,h=39,11; x,y=2,3; cols,rows=46,17; sentinel=(65536.,-32.,0.5,0.625); expected=(8.125,8.125,0.375,1.)
buf=b''.join(struct.pack('<4f',*sentinel) for _ in range(rows*cols)); got=C.create_string_buffer(len(buf)); devices=[]
for i in range(count.value):
    dev=I(); name=C.create_string_buffer(256); context=V(); dst=L()
    check(bind(c,'cuDeviceGet',C.POINTER(I),I)(C.byref(dev),i)); check(bind(c,'cuDeviceGetName',V,I,I)(name,len(name),dev))
    check(bind(c,'cuCtxCreate_v2',C.POINTER(V),U,I)(C.byref(context),0,dev))
    try:
        check(bind(c,'cuMemAlloc_v2',C.POINTER(L),Z)(C.byref(dst),len(buf)))
        try:
            check(bind(c,'cuMemcpyHtoD_v2',L,V,Z)(dst,buf,len(buf)))
            assert fill(V(dst.value),cols*16-1,x,y,w,h)==1
            check(fill(V(dst.value),cols*16,x,y,w,h))
            check(bind(c,'cuMemcpyDtoH_v2',V,L,Z)(got,dst,len(buf)))
            assert list(struct.iter_unpack('<4f',got.raw))==[expected if x<=j<x+w and y<=k<y+h else sentinel for k in range(rows) for j in range(cols)]
            devices.append({'name':name.value.decode(),'valid_region_exact':w*h,'untouched_guard_exact':cols*rows-w*h})
        finally: check(bind(c,'cuMemFree_v2',L)(dst))
    finally: check(bind(c,'cuCtxDestroy_v2',V)(context))
    assert fill(V(1),cols*16,x,y,w,h)==2
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
print(json.dumps({'status':'PASS standalone CUDA; Resolve OFX host untested here','id':ids[0],'devices':devices,'ofx_sha256':h(P),'harness_sha256':h(H)},indent=2))
