from pathlib import Path
import ctypes as c,json,random,struct,time,concurrent.futures,math
R=Path(__file__).resolve().parents[1]
schema=json.loads((R.parents[1]/'parameters/press_machine_v2.json').read_text())
default=[p['default'] for p in schema];index={p['id']:i for i,p in enumerate(schema)}
lib=c.CDLL(str(R/'build/Release/PressMachineParity.dll'))
lib.pm_eval.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.c_int,c.POINTER(c.c_float)]
lib.pm_baseline.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.POINTER(c.c_float)]
lib.pm_identity.argtypes=[c.POINTER(c.c_double)];lib.pm_identity.restype=c.c_int
def state(**kw):
 v=default[:]
 for name,value in kw.items():v[index[name]]=value
 return v
states=[
 default,state(pm_pre=130,pm_compression=50,pm_density=40,pm_chroma=20,pm_hue_compression=70,pm_hue_angle=30,pm_hue_points_index=2,pm_sat_skin=65,pm_density_skin=40),
 state(pm_pre=130,pm_compression=50,pm_density=40,pm_chroma=20,pm_hue_compression=70,pm_hue_angle=30,pm_hue_points_index=2,pm_sat_skin=65,pm_density_skin=40,pm_db=1),
 state(pm_density=-300,pm_chroma=100,pm_response=4,pm_highlight=100,pm_hr=100),
 state(pm_density=300,pm_chroma=-100,pm_response=1,pm_shadow=100,pm_sr=100),
 state(pm_sd_t=.25,pm_sd_k=.18,pm_hd_t=.7,pm_hd_k=.18),
]
for points in range(5):states.append(state(pm_hue_points_index=points,pm_hue_compression=50,pm_hue_angle=80))
def eval(x,v,premult=0,baseline=False):
 a=(c.c_float*4)(*x);b=(c.c_double*25)(*v);o=(c.c_float*4)()
 if baseline:lib.pm_baseline(a,b,o)
 else:lib.pm_eval(a,b,premult,o)
 return tuple(o)
pack=lambda v:struct.pack('4f',*v)
rng=random.Random(19382145)
samples=[(0.,0.,0.,1.),(-0.,-0.,-0.,1.),(.18,.18,.18,1.),(.4,.2,.1,1.),(-.1,.3,1.5,1.)]
samples += [tuple(rng.uniform(-.2,1.8) for _ in range(3))+(1.,) for _ in range(45)]
pairs=[(0,0),(1,1),(2,2),(3,3),(0,4)]
jobs=[]
for ig,it in pairs:
 for si,v in enumerate(states):
  v=v[:];v[index['pmi_ig']]=ig;v[index['pmi_it']]=it
  for x in samples:jobs.append((x,v))
# Explicit output profiles ensure output conversion is not suppressed by IsIdentity.
for og in range(1,5):
 for ot in range(1,6):
  v=state(pmi_og=og,pmi_ot=ot)
  for x in samples[:5]:jobs.append((x,v))
def check(job):
 x,v=job;old=eval(x,v,baseline=True);new=eval(x,v)
 assert pack(new)==pack(old),(x,v,new,old)
 assert math.isfinite(new[0]) and math.isfinite(new[1]) and math.isfinite(new[2])
 return max(abs(a-b) for a,b in zip(old,new))
start=time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:errors=list(pool.map(check,jobs))
alpha_tests=0
for alpha in (0.,.125,.5,1.,-1.):
 for v in states:
  x=(.13*alpha,.07*alpha,.02*alpha,alpha)
  y=eval(x,v,premult=1)
  assert struct.pack('f',y[3])==struct.pack('f',alpha)
  if alpha==0.:assert pack(y)==pack(x)
  else:
   # Recreate the exact float32 unpremultiplication and remultiplication.
   f=lambda n:c.c_float(n).value
   a=f(alpha);inv=f(1./a) if a!=1. else 1.
   straight=[f(f(q)*inv) for q in x[:3]]+[a]
   z=eval(straight,v);want=[f(q*a) for q in z[:3]]+[a]
   assert pack(y)==pack(want),(alpha,y,want)
  alpha_tests+=1
assert lib.pm_identity((c.c_double*25)(*default))==1
assert lib.pm_identity((c.c_double*25)(*state(pmi_og=2)))==0
assert lib.pm_identity((c.c_double*25)(*state(pm_hue_compression=1)))==0
assert lib.pm_identity((c.c_double*25)(*state(pm_density=25,pm_db=1)))==1
result=dict(status='PASS',baseline='19382145',bit_exact_cases=len(jobs),max_error=max(errors),threads=4,profiles=pairs,alpha_cases=alpha_tests,identity_cases=4,seconds=time.perf_counter()-start,scope='CPU compiled baseline vs parameterized shared core; not Resolve Host acceptance')
(R/'results/CPU_PARITY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
