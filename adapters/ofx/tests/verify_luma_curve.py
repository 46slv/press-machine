"""Provisional two-control curve; no chosen final look or Host acceptance claim."""
from pathlib import Path
import argparse,ctypes as C,hashlib,json,math,os,random,struct
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
schema=json.loads((REPO/'parameters/press_machine_v3_curve.json').read_text())
old_schema=json.loads((REPO/'parameters/press_machine_v3.json').read_text())
assert len(schema)==30
# Only UI grouping changed in the legacy27 prefix; IDs/defaults/ranges/model stay frozen.
assert [{k:v for k,v in p.items() if k!='group'} for p in schema[:27]] == [{k:v for k,v in p.items() if k!='group'} for p in old_schema]
default={p['id']:p['default'] for p in schema}
libpath=R/'build'/('VNextNative.dll' if os.name=='nt' else 'libvnext_native.so')
lib=C.CDLL(str(libpath));D=C.POINTER(C.c_double);F=C.POINTER(C.c_float)
lib.pm_vnext_curve.argtypes=[C.c_double]*3+[D]
lib.pm_vnext_hue_curve.argtypes=[D]+[C.c_double]*2+[C.c_int]+[C.c_double]*5+[D]
lib.pm_vnext_y.argtypes=[D];lib.pm_vnext_y.restype=C.c_double
lib.pm_eval30.argtypes=[F,D,C.c_int,F];lib.pm_dctl_eval30.argtypes=[F,D,F];lib.pm_identity30.argtypes=[D]
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
 o=(C.c_float*4)();lib.pm_eval30((C.c_float*4)(*x),p,0,o);return bytes(o),tuple(o)
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
 lib.pm_eval30(x,p,0,a);lib.pm_dctl_eval30(x,p,b)
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
for kw in [dict(pm_luma_pivot_ev=-6),dict(pm_luma_width=4)]:check(lib.pm_identity30(params(**kw))==1,'curve_only_creative_identity')


# Independent alpha-wrapper and final tonal-desaturation regression gates.
# The shared product math remains unchanged; this exercises the generated
# straight-RGB DCTL adapter against the OFX CPU premultiplication wrapper.
lib.pm_vnext_stages30.argtypes=[D,D,D]
lib.pm_eval30.restype=None;lib.pm_dctl_eval30.restype=None;lib.pm_vnext_stages30.restype=None
def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def f32bits(x): return struct.pack('<f',float(x))
def f32_order(x):
 u=struct.unpack('<I',f32bits(x))[0]
 return 0x80000000-u if (u&0x80000000) else 0x80000000+u
def f32_ulp(a,b): return abs(f32_order(a)-f32_order(b))
def dctl_rgb(rgb,p):
 src=(C.c_float*4)(*rgb,1.0);out=(C.c_float*4)()
 lib.pm_dctl_eval30(src,p,out)
 return tuple(out[:3])
curve_p=params(pmi_it=4,pm_hue_angle=37,pm_hue_pattern=2,pm_hue_compression=70,
               pm_hue_bias=-25,pm_luma_split=180,pm_luma_pivot_ev=1.25,pm_luma_width=.65)
default_curve_p=params(pmi_it=4,pm_hue_angle=37,pm_hue_pattern=2,pm_hue_compression=70,
                       pm_hue_bias=-25,pm_luma_split=180,pm_luma_pivot_ev=0,pm_luma_width=1)
alpha_bits=[('min_subnormal',0x00000001),('17_subnormal',0x00000011),
            ('max_subnormal',0x007fffff),('min_normal',0x00800000),('normal_quarter',0x3e800000)]
premult_colors=[(1.,3.,5.),(2.,1.,3.),(1.5,.75,3.25)]
max_premult_ulp=0;changed_curve_cases=0;premult_case_count=0
for alpha_name,bits in alpha_bits:
 alpha=struct.unpack('<f',struct.pack('<I',bits))[0]
 for rgb in premult_colors:
  src=[f32(alpha*x) for x in rgb]+[alpha]
  recovered=[f32(src[c]/alpha) for c in range(3)]
  curved=dctl_rgb(recovered,curve_p);plain=dctl_rgb(recovered,default_curve_p)
  changed=any(f32bits(curved[c])!=f32bits(plain[c]) for c in range(3))
  changed_curve_cases+=int(changed)
  check(changed,'curve_premult_nondefault_effect',str((alpha_name,rgb)))
  want=[f32(curved[c]*alpha) for c in range(3)]+[alpha]
  actual=(C.c_float*4)();lib.pm_eval30((C.c_float*4)(*src),curve_p,1,actual)
  check(all(math.isfinite(x) for x in actual),'curve_premult_finite',str((alpha_name,rgb)))
  check(f32bits(actual[3])==f32bits(alpha),'curve_premult_alpha_exact',str(alpha_name))
  error=max(f32_ulp(actual[c],want[c]) for c in range(3));max_premult_ulp=max(max_premult_ulp,error)
  check(error<=1,'curve_premult_vs_straight_DCTL',str((alpha_name,rgb,error)))
  premult_case_count+=1
hidden=(C.c_float*4)(-3.5,1e-7,7.0,0.0);hidden_out=(C.c_float*4)()
lib.pm_eval30(hidden,curve_p,1,hidden_out)
check(all(f32bits(hidden[i])==f32bits(hidden_out[i]) for i in range(4)),
      'premult_alpha0_hidden_RGB_exact')
check(changed_curve_cases==premult_case_count,'all_subnormal_curve_cases_active')

# Independent binary64 oracle for final desaturation. These DWG-Y and DI-level
# constants are the shared scalar contract; the oracle does not call product
# code for Y, level, smoothstep, mask composition, or output reconstruction.
wr=0.27411851286888123-2.8688812436783451e-09
wg=0.87363189458847046+5.4115295577972233e-09
wb=-0.14775040745735168-2.5426483141188783e-09
level_scale=0.073292478919029236+1.0809707573500305e-09
def ref_y(rgb): return wr*rgb[0]+wg*rgb[1]+wb*rgb[2]
def ref_smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)))
 return t*t*(3.-2.*t)
def ref_level(y):
 if y<=0.0026240900624543428:
  return y*(10.444268226623535+3.2337646516111818e-07)
 return (math.log2(y+0.0074999998323619366+1.6763806315323038e-10)+7.)*level_scale
def ref_shadow_keep(level,t,k):
 if t==0. or level>=t:return 1.
 lo=max(0.,t-k)
 if k==0. or level<=lo:return 0.
 return ref_smooth(lo,t,level)
def ref_highlight_keep(level,t,k):
 if t==1. or level<=t:return 1.
 hi=min(1.,t+k)
 if k==0. or level>=hi:return 0.
 return 1.-ref_smooth(t,hi,level)
def ref_final_desat(rgb,st,sk,ht,hk):
 y=ref_y(rgb)
 if y<=0.:return ([y,y,y] if st>0. else list(rgb)),y,None,0.,1.
 level=ref_level(y);ks=ref_shadow_keep(level,st,sk);kh=ref_highlight_keep(level,ht,hk);keep=ks*kh
 return ([y*(1.-keep)+c*keep for c in rgb],y,level,ks,kh)
def rgb_for_level(level):
 y=2.**(level/level_scale-7.)-0.0075
 r=2.*y;b=.5*y;g=(y-wr*r-wb*b)/wg
 return [r,g,b]
desat_cases=[
 ('highlight_knee_low',.49,0.,.18,.50,.25),
 ('highlight_knee_mid',.625,0.,.18,.50,.25),
 ('highlight_knee_high',.80,0.,.18,.50,.25),
 ('highlight_hard_below',.49,0.,.18,.50,0.),
 ('highlight_hard_above',.51,0.,.18,.50,0.),
 ('shadow_knee_low',.10,.50,.25,1.,.18),
 ('shadow_knee_mid',.375,.50,.25,1.,.18),
 ('shadow_knee_high',.51,.50,.25,1.,.18),
 ('shadow_hard_below',.49,.50,0.,1.,.18),
 ('shadow_hard_above',.51,.50,0.,1.,.18),
 ('overlap_keep_product',.60,.70,.40,.50,.40)]
max_desat_error=0.;overlap_keep=None
for name,target,st,sk,ht,hk in desat_cases:
 rgb=rgb_for_level(target);p=params(pmi_it=4,pm_sd_t=st,pm_sd_k=sk,pm_hd_t=ht,pm_hd_k=hk)
 x=arr(rgb);out=(C.c_double*17)();lib.pm_vnext_stages30(x,p,out)
 look=list(out[9:12]);actual=list(out[12:15])
 check(max(abs(look[i]-rgb[i]) for i in range(3))<2e-8,
       'final_desat_test_input_unchanged',name)
 expected,y,measured,ks,kh=ref_final_desat(rgb,st,sk,ht,hk)
 error=max(abs(actual[i]-expected[i]) for i in range(3));max_desat_error=max(max_desat_error,error)
 check(error<1e-6*max(1.,max(abs(v) for v in rgb)),
       'final_desat_independent_binary64_oracle',str((name,measured,error)))
 if name=='overlap_keep_product':
  overlap_keep=ks*kh
  check(0.<overlap_keep<1. and abs(overlap_keep-min(ks,kh))>1e-3,
        'final_desat_overlap_is_product',str((ks,kh,overlap_keep)))
report_extra={'premult_curve_cases':premult_case_count,
              'premult_alpha_classes':[x[0] for x in alpha_bits],
              'nondefault_curve_effect_cases':changed_curve_cases,
              'max_premult_RGB_ULP_vs_generated_DCTL':max_premult_ulp,
              'alpha0_hidden_RGB_exact':True,
              'independent_final_desat_cases':len(desat_cases),
              'overlap_keep_product':overlap_keep,
              'max_final_desat_abs_RGB_error':max_desat_error,
              'final_desat_oracle':'independent binary64 DWG-Y / DI-level / smoothstep / keep-product / RGB reconstruction'}

parser=argparse.ArgumentParser();parser.add_argument('--baseline-dll');args=parser.parse_args()
baseline={'run':False,'scope':'Optional pinned27-value adapter binary is not available in ordinary CI.'}
if args.baseline_dll:
 bp=Path(args.baseline_dll);bh=hashlib.sha256(bp.read_bytes()).hexdigest()
 assert bh=='a7870fc3debb7ea5c9cda96c15df72d1c8d938cebf9d30f3b6091cf5b4dc9b8e'
 old=C.CDLL(str(bp));old.pm_eval.argtypes=[F,D,C.c_int,F]
 for i in range(1200):
  p=default.copy();p.update(pmi_it=4,pm_pre=rng.uniform(0,200),pm_threshold=rng.uniform(0,100),pm_compression=rng.uniform(0,100),pm_hue_angle=rng.uniform(0,360),pm_hue_pattern=i%6,pm_hue_compression=rng.uniform(0,100),pm_hue_bias=rng.uniform(-100,100),pm_luma_split=rng.uniform(-300,300),pm_density=rng.uniform(-300,300),pm_chroma=rng.uniform(-100,100),pm_sat_skin=rng.choice([0,50,100]),pm_density_skin=rng.choice([0,50,100]))
  x=(C.c_float*4)(*[rng.uniform(-2,8) for _ in range(3)],rng.random());a=(C.c_float*4)();b=(C.c_float*4)()
  old.pm_eval(x,arr([p[z['id']] for z in old_schema]),i%2,a);lib.pm_eval30(x,arr([p[z['id']] for z in schema]),i%2,b)
  check(bytes(a)==bytes(b),'old27_adapter_default_curve_RGBA_exact')
 baseline={'run':True,'sha256':bh,'cases':1200,'RGBA_words_exact':4800,'scope':'Same supported values with new curve at0/1. Random signed linear input and straight/premult modes. Not whole-domain equivalence.'}
report={'status':'PASS','checks':sum(counts.values()),'groups':counts,'max_scalar_absolute_error':max_scalar,'max_hue_Y_normalized_error':max_y,'additional_regressions':report_extra,'parameters':schema[27:],'baseline':baseline,'library_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),'schema_sha256':hashlib.sha256((REPO/'parameters/press_machine_v3_curve.json').read_bytes()).hexdigest(),'curve_source_sha256':hashlib.sha256((REPO/'core/press_machine/HueLumaCurve.dctlh').read_bytes()).hexdigest(),'scope':'Provisional curve CPU/reference and CPU-compiled generated-DCTL checks, including premultiplied subnormal-alpha coverage and an independent final-desaturation semantic oracle. Ranges and shape remain adjustable; no Resolve UI, persistence, native pixels, product OFX Host, footage or 4K acceptance claim.'}
out=R/('results/v3_curve/LUMA_CURVE_BASELINE.json' if args.baseline_dll else 'results/v3_curve/LUMA_CURVE.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
