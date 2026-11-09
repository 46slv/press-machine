from pathlib import Path
import ctypes as c,json,math,struct,os,sys
R=Path(__file__).resolve().parents[1]
schema=json.loads((R.parents[1]/'parameters/press_machine_v3.json').read_text());default=[p['default'] for p in schema];idx={p['id']:i for i,p in enumerate(schema)}
path=Path(sys.argv[1]) if len(sys.argv)>1 else R/('build/Release/PressMachineParity.dll' if os.name=='nt' else 'build/libvnext_native.so')
lib=c.CDLL(str(path));lib.pm_eval.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.c_int,c.POINTER(c.c_float)]
f=lambda x:c.c_float(x).value
def run(x,v,m):
 o=(c.c_float*4)();lib.pm_eval((c.c_float*4)(*x),(c.c_double*len(schema))(*v),m,o);return tuple(o)
pack=lambda x:struct.pack('4f',*x)
states=[default]
for kw in ({'pm_compression':50},{'pm_hue_compression':50,'pm_hue_pattern':0},{'pm_density':40,'pm_chroma':20},{'pm_hue_bias':100},{'pm_luma_split':300},{'pm_hue_bias':-100,'pm_luma_split':-300}):
 v=default[:]
 for k,value in kw.items():v[idx[k]]=value
 states.append(v)
cases=[]
for a in [float.fromhex('0x1p-149'),float.fromhex('0x1p-140'),1e-40,1e-30,1e-10,.3,1.,-1e-40,2.]:
 a=f(a);cases.append(tuple(map(f,(a,a*.5,0.,a))))
cases.extend([(1.,.5,0.,f(1e-40)),(0.,0.,0.,0.)])
maxerr=0.
for x in cases:
 for si,v in enumerate(states):
  y=run(x,v,1)
  assert all(math.isfinite(z) for z in y),(x,si,y)
  assert pack([0.,0.,0.,y[3]])==pack([0.,0.,0.,x[3]])
  if si==0:assert pack(x)==pack(y),(x,y)
  if x[3] not in (0.,1.):
   straight=tuple(f(q/x[3]) for q in x[:3])+(x[3],)
   if not all(math.isfinite(z) for z in straight[:3]):assert pack(x)==pack(y)
   else:
    z=run(straight,v,0);want=tuple(f(q*x[3]) for q in z[:3])+(x[3],)
    if not all(math.isfinite(q) for q in want[:3]):want=x
    error=max(abs(a-b) for a,b in zip(y,want));maxerr=max(maxerr,error)
    assert error<=max(1e-44,max(abs(q) for q in want[:3])*2**-22),(x,si,y,want,error)
result=dict(status='PASS',cases=len(cases)*len(states),subnormal_identity_word_exact=True,finite_rgba_preserved=True,independent_ratio_reference='Python double division then binary32 rounding; no reciprocal',max_error=maxerr)
(R/'results/v3/ALPHA_EXTREMES.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
