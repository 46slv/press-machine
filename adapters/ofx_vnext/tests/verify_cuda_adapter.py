from pathlib import Path
import ctypes as c,json,time,math,struct,random
R=Path(__file__).resolve().parents[1]
schema=json.loads((R.parents[1]/'parameters/press_machine_vnext.json').read_text())
P=type('Parameters',(c.Structure,),{'_fields_':[(p['id'],c.c_float if p['kind']=='double' else c.c_int) for p in schema]})
assert c.sizeof(P)==4*len(schema)
default=[p['default'] for p in schema];idx={p['id']:i for i,p in enumerate(schema)}
def state(**kw):
 v=default[:]
 for k,x in kw.items():v[idx[k]]=x
 return v
states=[
 default,
 state(pm_pre=130,pm_compression=50,pm_threshold=55,pm_sat_skin=50,pm_hue_pattern=1,pm_hue_compression=70,pm_hue_angle=30,pm_hue_bias=20,pm_luma_split=100,pm_density=80,pm_chroma=20,pm_density_skin=40),
 state(pm_density=-300,pm_chroma=100,pm_response=4,pm_highlight=100,pm_hr=100),
 state(pm_density=300,pm_chroma=-100,pm_response=1,pm_shadow=100,pm_sr=100),
 state(pm_sd_t=.25,pm_sd_k=.18,pm_hd_t=.7,pm_hd_k=.18)
]
for pattern in range(6):
 states.append(state(pm_hue_pattern=pattern,pm_hue_compression=50,pm_hue_angle=80,pm_hue_bias=-50,pm_luma_split=200))
cpu=c.CDLL(str(R/'build/Release/PressMachineVNextParity.dll'))
cpu.pm_vnext_eval.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.c_int,c.POINTER(c.c_float)]
adapter=c.CDLL(str(R/'build/Release/PressMachineVNextCudaAdapterTest.dll'))
ptr=c.c_void_p;I=c.c_int;U=c.c_uint;L=c.c_size_t;Q=c.c_ulonglong
adapter.pm_vnext_cuda_adapter.argtypes=[ptr,ptr,ptr,c.c_longlong,c.c_longlong]+[I]*11+[c.POINTER(c.c_double)]
adapter.pm_vnext_cuda_adapter.restype=I
D=c.WinDLL('nvcuda.dll')
def fn(name,args):
 f=getattr(D,name);f.argtypes=args;f.restype=c.c_int;return f
init=fn('cuInit',[U]);getdev=fn('cuDeviceGet',[c.POINTER(I),I]);create=fn('cuCtxCreate_v2',[c.POINTER(ptr),U,I]);destroy=fn('cuCtxDestroy_v2',[ptr])
namefn=fn('cuDeviceGetName',[c.c_char_p,I,I]);alloc=fn('cuMemAlloc_v2',[c.POINTER(Q),L]);free=fn('cuMemFree_v2',[Q])
htod=fn('cuMemcpyHtoD_v2',[Q,ptr,L]);dtoh=fn('cuMemcpyDtoH_v2',[ptr,Q,L])
streamcreate=fn('cuStreamCreate',[c.POINTER(ptr),U]);streamsync=fn('cuStreamSynchronize',[ptr]);streamdestroy=fn('cuStreamDestroy_v2',[ptr])
def ok(status):assert status==0,'CUDA status '+str(status)
ok(init(0));dev=I();ok(getdev(c.byref(dev),0));name=c.create_string_buffer(256);ok(namefn(name,256,dev))
context=ptr();src=Q();dst=Q();teststream=ptr();start=time.perf_counter();ok(create(c.byref(context),0,dev))
try:
 ok(streamcreate(c.byref(teststream),1))
 sw,sh=6,5;dw,dh=12,10;sp=(sw*4+7)*4;dp=(dw*4+11)*4
 source=(c.c_float*(sp//4*sh))();target=(c.c_float*(dp//4*dh))();rng=random.Random(20261109)
 for y in range(sh):
  for x in range(sw):
   alpha=[0.,.5,1.,1e-40,1e-10,-1e-40][x]
   v=([alpha,alpha*.5,0.,alpha] if 0<abs(alpha)<1e-8 else [rng.uniform(-.2,1.8) for _ in range(3)]+[alpha])
   for ch in range(4):source[y*(sp//4)+x*4+ch]=v[ch]
 ok(alloc(c.byref(src),c.sizeof(source)));ok(alloc(c.byref(dst),c.sizeof(target)));ok(htod(src,source,c.sizeof(source)))
 maxerr=0.;cases=0;alpha_words=0;sentinels=0;first=0.
 for ig,it in [(0,0),(1,1),(2,2),(3,3),(0,4)]:
  for vi,v in enumerate(states):
   v=v[:];v[idx['pmi_ig']]=ig;v[idx['pmi_it']]=it
   for premult in [0,1]:
    for i in range(len(target)):target[i]=-99.
    ok(htod(dst,target,c.sizeof(target)))
    stream=teststream if vi%2 else None;t=time.perf_counter()
    rc=adapter.pm_vnext_cuda_adapter(stream,ptr(src.value),ptr(dst.value),sp,dp,8,17,14,22,5,15,6,16,16,24,premult,(c.c_double*len(v))(*v));assert rc==0
    if cases==0:first=time.perf_counter()-t
    if stream:ok(streamsync(stream))
    ok(dtoh(target,dst,c.sizeof(target)))
    for y in range(dh):
     for x in range(dw):
      ax=x+5;ay=y+15;o=tuple(target[y*(dp//4)+x*4+ch] for ch in range(4))
      if 6<=ax<16 and 16<=ay<24:
       if 8<=ax<14 and 17<=ay<22:
        ins=(c.c_float*4)(*[source[(ay-17)*(sp//4)+(ax-8)*4+ch] for ch in range(4)]);want=(c.c_float*4)()
        cpu.pm_vnext_eval(ins,(c.c_double*len(v))(*v),premult,want)
        error=max(abs(o[ch]-want[ch]) for ch in range(3));maxerr=max(maxerr,error)
        assert all(math.isfinite(z) for z in o) and error<=2**-13,(ig,it,vi,premult,ax,ay,o,tuple(want),error)
        assert struct.pack('f',o[3])==struct.pack('f',want[3]);alpha_words+=1;cases+=1
       else:assert o==(0.,0.,0.,0.)
      else:
       assert o==(-99.,-99.,-99.,-99.);sentinels+=4
 result={'status':'PASS','device':name.value.decode(),'source':'actual vNext CudaRunner adapter / embedded compute75 PTX','gpu_pixel_cases':cases,'preserved_alpha_words':alpha_words,'outside_roi_sentinel_words':sentinels,'profiles':5,'states':len(states),'premult_modes':2,'max_error':maxerr,'tolerance':2**-13,'first_adapter_call_seconds':first,'stream_modes':['default-completed','nonnull-Host-stream'],'seconds':time.perf_counter()-start,'scope':'independent NVIDIA context; actual CUDA adapter parity, not Resolve Host acceptance'}
 (R/'results').mkdir(exist_ok=True);(R/'results/CUDA_ADAPTER_VNEXT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
finally:
 if src.value:free(src)
 if dst.value:free(dst)
 if teststream.value:streamdestroy(teststream)
 if context.value:destroy(context)
