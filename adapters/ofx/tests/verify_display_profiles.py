"""Independent SDR transfer/matrix/boundary and active profile oracle. No Host claim."""
from pathlib import Path
import runpy,ctypes as C,math,struct,json,hashlib
R=Path(__file__).resolve().parents[1]
n=runpy.run_path(str(R/'tests/verify_rec709.py'));lib=n['lib'];schema=n['schema'];par=n['par'];mv=n['mv'];mul=n['mul'];inv=n['inv'];xyz=n['xyz'];dwg=n['dwg'];pixels=n['pixels'];F=n['F'];D=n['D'];counts={};errors={}
lib.pm_display_matrix.argtypes=[D,C.c_int,C.c_int,D];lib.pm_display_transfer.argtypes=[C.c_float,C.c_int,C.c_int];lib.pm_display_transfer.restype=C.c_double
xy={4:[('.64','.33'),('.30','.60'),('.15','.06')],5:[('.708','.292'),('.170','.797'),('.131','.046')],6:[('.68','.32'),('.265','.69'),('.15','.06')]};to={g:mul(inv(dwg),xyz(v)) for g,v in xy.items()};back={g:mul(inv(xyz(v)),dwg) for g,v in xy.items()}
def check(x,k):counts[k]=counts.get(k,0)+1;assert x,k
def f32(x):return C.c_float(x).value
def neighbor(v,d):
 bits=struct.unpack('<I',struct.pack('<f',v))[0];return struct.unpack('<f',struct.pack('<I',bits+d))[0]
A=1.09929682680944;B=.018053968510807
def transfer(v,t,encode):
 if v==0:return v
 a=abs(v)
 if t in (5,6):y=a**((1/(2.4 if t==5 else 2.2)) if encode else (2.4 if t==5 else 2.2))
 elif t==7:y=(12.92*a if a<=.0031308 else 1.055*a**(1/2.4)-.055) if encode else (a/12.92 if a<=.04045 else ((a+.055)/1.055)**2.4)
 else:y=(4.5*a if a<=B else A*a**.45-(A-1)) if encode else (a/4.5 if a<=4.5*B else ((a+(A-1))/A)**(1/.45))
 return math.copysign(y,v)
knots=[0.,1e-45,1e-20,.0031308,.04045,B,4.5*B,1.,2.,4.,16.];probes=[]
for v in knots:
 vals=[f32(v)] if v==0 else [neighbor(f32(v),d) for d in [-1,0,1]]
 for z in vals:probes.extend([z,-z])
for t in range(5,9):
 for encode in [0,1]:
  for v in probes:
   y=lib.pm_display_transfer(v,t,encode);ref=transfer(v,t,encode);e=abs(y-ref);errors['transfer_abs']=max(errors.get('transfer_abs',0),e);check(e<=2e-6*abs(ref)+1e-12,'analytic_transfer_boundary')
   if v==0:check(math.copysign(1,y)==math.copysign(1,v),'signed_zero')
 for v in [0.,.001,.02,.2,.5,1.,-0.2,2.]:
  y=lib.pm_display_transfer(f32(v),t,0);z=lib.pm_display_transfer(f32(y),t,1);check(abs(z-f32(v))<2e-6,'transfer_roundtrip')
for g in xy:
 for x in pixels:
  for inverse,m in [(0,to[g]),(1,back[g])]:
   out=(C.c_double*3)();lib.pm_display_matrix((C.c_double*3)(*x),g,inverse,out);check(max(abs(a-b) for a,b in zip(out,mv(m,x)))<2e-11*max(1,*map(abs,x)),'rational_gamut_matrix')
 for it in range(5,9):
  for ot in range(5,9):
   for og in xy:
    for density in [-100,100]:
     p=par(pmi_ig=g,pmi_it=it,pmi_og=og+1,pmi_ot=ot+1,pm_pre=120,pm_compression=40,pm_makeup=150,pm_hue_bias=-25,pm_luma_split=100,pm_density=density,pm_chroma=-50)
     for x in [[.02,.04,.06],[.5,.2,.1],[1.,.5,.05],[-.02,.3,1.2],[.18]*3]:
      x=[f32(v) for v in x];o=n['eval'](lib,x,p);linear=[transfer(v,it,False) for v in x];st=(C.c_double*17)();lib.pm_vnext_stages30((C.c_double*3)(*mv(to[g],linear)),p,st);expected=[transfer(v,ot,True) for v in mv(back[og],list(st[12:15]))];e=max(abs(o[i]-expected[i]) for i in range(3));errors['active_profile_abs']=max(errors.get('active_profile_abs',0),e);check(e<2**-13,'active_profile_independent_oracle');d=(C.c_float*4)();lib.pm_dctl_eval30((C.c_float*4)(*x,1),p,d);check(bytes(o)==bytes(d),'display_generated_DCTL_exact');check(all(math.isfinite(v) for v in o),'display_active_finite')
  for x in [[-0.,.1,1.],[-.1,.3,2.],[1e-40]*3]:check(bytes(n['eval'](lib,x,par(pmi_ig=g,pmi_it=it)))==bytes((C.c_float*4)(*x,1)),'display_neutral_exact')
# Overflow cannot silently create Inf in a rendered pixel; existing domain fallback returns original.
for t in [5,6,7,8]:
 x=[f32(3e38)]*3;p=par(pmi_ig=4,pmi_it=t,pm_hue_bias=10);o=n['eval'](lib,x,p);check(bytes(o)==bytes((C.c_float*4)(*x,1)),'unrepresentable_decode_fallback')
check(len(schema[0]['options'])==7 and len(schema[1]['options'])==9 and len(schema[2]['options'])==8 and len(schema[3]['options'])==10,'append_only_counts')
r=dict(status='PASS_FOCUSED_SDR_DISPLAY_PROFILES',counts=counts,max_errors=errors,native_library_sha256=hashlib.sha256(n['native'].read_bytes()).hexdigest(),limits='Native/generatedDCTL CPU. New signed extension and continuous Rec709 OETF explicit. Gamma2.4 ideal zero-black; no PQ/HLG/range scaling/gamut mapping or broad Host claim.')
(R/'results/v3_curve/DISPLAY_PROFILES.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
