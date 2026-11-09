from pathlib import Path
import ctypes as c,json,math,os,struct
REPO=Path(__file__).resolve().parents[3]
ADAPTER=Path(__file__).resolve().parents[1]
schema=json.loads((REPO/'parameters/press_machine_vnext.json').read_text());defaults=[p['default'] for p in schema];idx={p['id']:i for i,p in enumerate(schema)}
lib=c.CDLL(os.environ.get('PM_VNEXT_NATIVE',str(ADAPTER/'build/Release/PressMachineVNextParity.dll')))
lib.pm_vnext_eval.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.c_int,c.POINTER(c.c_float)]
lib.pm_vnext_identity.argtypes=[c.POINTER(c.c_double)];lib.pm_vnext_identity.restype=c.c_int
lib.pm_vnext_skin_mask.argtypes=[c.POINTER(c.c_float)];lib.pm_vnext_skin_mask.restype=c.c_float
lib.pm_vnext_stages.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.POINTER(c.c_float)]
def state(**kw):
 v=defaults[:]
 for k,x in kw.items():v[idx[k]]=x
 return v
def arr(v):return (c.c_double*len(v))(*v)
def eval(rgba,v,premult=0):
 i=(c.c_float*4)(*rgba);o=(c.c_float*4)();lib.pm_vnext_eval(i,arr(v),premult,o);return tuple(o)
def stages(rgb,v):
 i=(c.c_float*3)(*rgb);o=(c.c_float*21)();lib.pm_vnext_stages(i,arr(v),o);return [tuple(o[3*j+k] for k in range(3)) for j in range(7)]
pack=lambda x:struct.pack('4f',*x)
assert lib.pm_vnext_identity(arr(defaults))==1
for x in [(0.,0.,0.,1.),(.18,.18,.18,1.),(.7,.12,-.03,1.),(-.2,.6,1.4,.5)]: assert pack(eval(x,defaults))==pack(x)
base=state(pmi_it=4,pm_hue_pattern=2,pm_hue_angle=35,pm_luma_split=300)
a=eval((.04,.04,.04,1.),base);assert all(math.isfinite(x) for x in a[:3]) and pack(a)!=pack((.04,.04,.04,1.))
b=eval((.04,.04,.04,1.),base);assert pack(a)==pack(b)
split=state(pmi_it=4,pm_hue_angle=35,pm_hue_pattern=2,pm_luma_split=300)
weighted=state(pmi_it=4,pm_hue_angle=35,pm_hue_pattern=2,pm_luma_split=300,pm_density=100)
s=eval((.04,.04,.04,1.),split);d=eval((.04,.04,.04,1.),weighted);Y=lambda x:.27411851*x[0]+.87363190*x[1]-.14775041*x[2];assert Y(d)<Y(s),(s,d,Y(s),Y(d))
skin=(.4,.2,.12);mask=lib.pm_vnext_skin_mask((c.c_float*3)(*skin));assert 0<=mask<=1
for protect in (0.,50.,100.):
 v=state(pm_pre=150,pm_compression=60,pm_threshold=50,pm_sat_skin=protect);st=stages(skin,v);raw,cond=st[1],st[2];keep=1-(protect/100)*mask
 want=tuple(skin[i]+keep*(raw[i]-skin[i]) for i in range(3));assert max(abs(cond[i]-want[i]) for i in range(3))<3e-6
for protect in (0.,50.,100.):
 v=state(pm_hue_pattern=3,pm_hue_compression=80,pm_hue_bias=30,pm_luma_split=140,pm_density=90,pm_density_skin=protect);st=stages(skin,v);cond,density_raw,look=st[2],st[4],st[5];keep=1-(protect/100)*mask
 want=tuple(cond[i]+keep*(density_raw[i]-cond[i]) for i in range(3));assert max(abs(look[i]-want[i]) for i in range(3))<3e-6
states=[state(pmi_it=4,pm_hue_pattern=p,pm_hue_compression=strength,pm_hue_bias=-100,pm_luma_split=300,pm_density=300,pm_chroma=100) for p in range(6) for strength in (0,25,50,100)]
samples=[(.18,.18,.18,1.),(.7,.12,-.03,1.),(-.2,.6,1.4,1.),(3.,-.5,.2,1.)]
for v in states:
 for x in samples:
  o=eval(x,v);assert all(math.isfinite(y) for y in o) and o[3]==x[3]
v=state(pm_hue_pattern=4,pm_hue_compression=75,pm_luma_split=200,pm_density=-120)
for alpha in (0.,.125,.5,1.):
 x=(.2*alpha,.1*alpha,.04*alpha,alpha);o=eval(x,v,1);assert struct.pack('f',o[3])==struct.pack('f',alpha)
 if alpha==0:assert pack(o)==pack(x)
result={'status':'PASS','parameters':len(schema),'pattern_states':len(states),'samples_per_state':len(samples),'net_comp_skin_cases':3,'net_look_skin_cases':3,'post_hue_density_case':'PASS','alpha_cases':4,'skin_mask_sample':mask,'scope':'shared CPU vNext core; not CUDA or Resolve Host'}
(ADAPTER/'results').mkdir(exist_ok=True);(ADAPTER/'results/CPU_VNEXT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
