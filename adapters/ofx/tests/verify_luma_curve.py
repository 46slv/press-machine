"""Provisional two-control curve; no chosen final look or Host acceptance claim."""
from pathlib import Path
import argparse,ctypes as C,hashlib,json,math,os,random,struct
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
schema=json.loads((REPO/'parameters/press_machine_v3_curve.json').read_text())
old_schema=json.loads((REPO/'parameters/press_machine_v3.json').read_text())
assert len(schema)==29 and schema[:27]==old_schema
default={p['id']:p['default'] for p in schema}
libpath=R/'build'/('VNextNative.dll' if os.name=='nt' else 'libvnext_native.so')
lib=C.CDLL(str(libpath));D=C.POINTER(C.c_double);F=C.POINTER(C.c_float)
lib.pm_vnext_curve.argtypes=[C.c_double]*3+[D]
lib.pm_vnext_hue_curve.argtypes=[D]+[C.c_double]*2+[C.c_int]+[C.c_double]*5+[D]
lib.pm_vnext_y.argtypes=[D];lib.pm_vnext_y.restype=C.c_double
lib.pm_eval.argtypes=[F,D,C.c_int,F];lib.pm_dctl_eval.argtypes=[F,D,F];lib.pm_identity.argtypes=[D]
counts={};max_scalar=max_y=0.0
def check(ok,group,detail=''):
 counts[group]=counts.get(group,0)+1
 assert ok,(group,detail)
def arr(x):return (C.c_double*len(x))(*x)
def params(**kw):
 p=default.copy();p.update(kw);return arr([p[z['id']] for z in schema])
def curve(y,pivot,width):
 o=(C.c_double*2)();lib.pm_vnext_curve(y,pivot,width,o);return tuple(o)
def oracle(y,pivot,width):
 if y<=0:return -1.0
 pivot=C.c_float(pivot).value;width=C.c_float(width).value
 sy=math.sqrt(y);root=math.sqrt(.18)*2**(pivot/2)
 q=(sy-root)/(sy+root)
 return q/(width+(1-width)*abs(q))
def pixel(x,p):
 o=(C.c_float*4)();lib.pm_eval((C.c_float*4)(*x),p,0,o);return bytes(o),tuple(o)
ys=[-3e37,-1.,0.,1e-37,1e-12,.001,.18,.72,2.88,1e12,3e37]
ys += [.18*2**(-24+48*i/160) for i in range(161)]
for pivot in [-6.,-1.3,0.,1.3,6.]:
 for width in [.25,.5,1.,2.,4.]:
  prev=-1.
  for y in sorted(set(ys)):
   base,q=curve(y,pivot,width);want=oracle(y,pivot,width)
   e=abs(q-want);max_scalar=max(max_scalar,e)
   check(math.isfinite(q) and -1.000000000001<=q<=1.000000000001,'finite_bounded',str((y,pivot,width,q)))
   check(e<3e-12,'independent_curve_reference',str((y,pivot,width,q,want)))
   check(q>=prev-1e-13,'curve_monotonic');prev=q
   if pivot==0 and width==1:check(q==base,'default_scalar_exact')
  center=.18*2**C.c_float(pivot).value
  check(abs(curve(center,pivot,width)[1])<3e-13,'shifted_midpoint')
  for stop in [1.,4.,12.,24.]:
   a=curve(center*2**(-stop),pivot,width)[1];b=curve(center*2**stop,pivot,width)[1]
   check(abs(a+b)<3e-12,'symmetric_exposure_response')
for pivot,width in [(float('nan'),1),(float('inf'),1),(-7,1),(7,1),(0,.2),(0,5),(0,float('nan'))]:
 for y in [-1,0,.001,.18,3e37]:
  a,b=curve(y,pivot,width);check(a==b,'invalid_curve_legacy_fallback')

rng=random.Random(1110)
for i in range(300):
 p=params(pmi_it=4,pm_pre=rng.uniform(0,200),pm_threshold=rng.uniform(0,100),pm_compression=rng.uniform(0,100),
          pm_hue_angle=rng.uniform(0,360),pm_hue_pattern=i%6,pm_hue_compression=rng.uniform(0,100),
          pm_hue_bias=rng.uniform(-100,100),pm_luma_split=rng.uniform(-300,300),
          pm_luma_pivot_ev=rng.uniform(-6,6),pm_luma_width=rng.uniform(.25,4),pm_density=0,
          pm_sat_skin=rng.choice([0,50,100]),pm_density_skin=rng.choice([0,50,100]),
          pm_sd_t=rng.choice([0,.5]),pm_sd_k=.18)
 x=(C.c_float*4)(*[rng.uniform(-2,8) for _ in range(3)],rng.random());a=(C.c_float*4)();b=(C.c_float*4)()
 lib.pm_eval(x,p,0,a);lib.pm_dctl_eval(x,p,b)
 check(bytes(a)==bytes(b),'nondefault_generated_dctl_CPU_exact')
 check(all(math.isfinite(z) for z in a),'nondefault_pipeline_finite')
 check(struct.pack('f',a[3])==struct.pack('f',x[3]),'alpha_word_preserved')

colors=[[.7,.45,.3],[.18,.18,.18],[-1,.2,2],[20,12,-2],[1e-25,-2e-25,4e-25],[1e25,-2e25,4e25]]
for x in colors:
 y=lib.pm_vnext_y(arr(x))
 for pattern in range(6):
  for pivot,width in [(-6,.25),(0,1),(0,4),(6,4),(1.3,.5)]:
   out=(C.c_double*3)();lib.pm_vnext_hue_curve(arr(x),y,33,pattern,70,80,-300,pivot,width,out)
   check(all(math.isfinite(z) for z in out),'curve_hue_finite')
   err=abs(lib.pm_vnext_y(out)-y)/max(1,abs(y),*(abs(z) for z in x));max_y=max(max_y,err)
   check(err<3e-8,'curve_hue_Y_preserved',str(err))
for x in colors:
 expected,_=pixel(x+[1],params(pmi_it=4,pm_hue_pattern=1,pm_hue_compression=70,pm_hue_bias=80))
 for pivot,width in [(-6,.25),(0,1),(6,4),(1.3,.5),(float('nan'),1)]:
  got,_=pixel(x+[1],params(pmi_it=4,pm_hue_pattern=1,pm_hue_compression=70,pm_hue_bias=80,pm_luma_pivot_ev=pivot,pm_luma_width=width))
  check(got==expected,'Split_zero_curve_no_effect_exact')
base,_=pixel([.7,.45,.3,1],params(pmi_it=4,pm_luma_split=100))
for k,kw in [('pivot',dict(pm_luma_pivot_ev=2)),('width',dict(pm_luma_width=3))]:
 got,_=pixel([.7,.45,.3,1],params(pmi_it=4,pm_luma_split=100,**kw));check(got!=base,'UI_'+k+'_active_response')
for kw in [dict(pm_luma_pivot_ev=-6),dict(pm_luma_width=4)]:check(lib.pm_identity(params(**kw))==1,'curve_only_creative_identity')

parser=argparse.ArgumentParser();parser.add_argument('--baseline-dll');args=parser.parse_args()
baseline={'run':False,'scope':'Optional pinned27-value adapter binary is not available in ordinary CI.'}
if args.baseline_dll:
 bp=Path(args.baseline_dll);bh=hashlib.sha256(bp.read_bytes()).hexdigest()
 assert bh=='a7870fc3debb7ea5c9cda96c15df72d1c8d938cebf9d30f3b6091cf5b4dc9b8e'
 old=C.CDLL(str(bp));old.pm_eval.argtypes=[F,D,C.c_int,F]
 for i in range(1200):
  p=default.copy();p.update(pmi_it=4,pm_pre=rng.uniform(0,200),pm_threshold=rng.uniform(0,100),pm_compression=rng.uniform(0,100),pm_hue_angle=rng.uniform(0,360),pm_hue_pattern=i%6,pm_hue_compression=rng.uniform(0,100),pm_hue_bias=rng.uniform(-100,100),pm_luma_split=rng.uniform(-300,300),pm_density=rng.uniform(-300,300),pm_chroma=rng.uniform(-100,100),pm_sat_skin=rng.choice([0,50,100]),pm_density_skin=rng.choice([0,50,100]))
  x=(C.c_float*4)(*[rng.uniform(-2,8) for _ in range(3)],rng.random());a=(C.c_float*4)();b=(C.c_float*4)()
  old.pm_eval(x,arr([p[z['id']] for z in old_schema]),i%2,a);lib.pm_eval(x,arr([p[z['id']] for z in schema]),i%2,b)
  check(bytes(a)==bytes(b),'old27_adapter_default_curve_RGBA_exact')
 baseline={'run':True,'sha256':bh,'cases':1200,'RGBA_words_exact':4800,'scope':'Same supported values with new curve at0/1. Random signed linear input and straight/premult modes. Not whole-domain equivalence.'}
report={'status':'PASS','checks':sum(counts.values()),'groups':counts,'max_scalar_absolute_error':max_scalar,'max_hue_Y_normalized_error':max_y,'parameters':schema[27:],'baseline':baseline,'library_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),'schema_sha256':hashlib.sha256((REPO/'parameters/press_machine_v3_curve.json').read_bytes()).hexdigest(),'curve_source_sha256':hashlib.sha256((REPO/'core/press_machine/HueLumaCurve.dctlh').read_bytes()).hexdigest(),'scope':'Provisional curve CPU/reference and CPU-compiled generated-DCTL checks. Ranges and shape are adjustable starting points, not final design. Resolve29-control UI, persistence, native pixels, product OFX Host, footage and4K not established by this report.'}
out=R/('results/v3_curve/LUMA_CURVE_BASELINE.json' if args.baseline_dll else 'results/v3_curve/LUMA_CURVE.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
