"""Independent chromaticity oracle, active output-Same and optional old-binary regression. Not Host acceptance."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,ctypes as C,json,random,math,hashlib,struct,os,subprocess
R=Path(__file__).resolve().parents[1];schema=json.loads((R.parents[1]/'parameters/press_machine_v3_curve.json').read_text())
a=argparse.ArgumentParser();a.add_argument('--legacy-library');args=a.parse_args()
build=R/'build';build.mkdir(exist_ok=True);native=build/('Rec709Native.dll' if os.name=='nt' else 'librec709_native.so')
command=(['cl','/nologo','/O2','/EHsc','/std:c++17','/fp:strict','/LD',str(R/'tests/Rec709Native.cpp'),'/link','/OUT:'+str(native)] if os.name=='nt' else ['g++','-O2','-std=c++17','-shared','-fPIC','-ffp-contract=off',str(R/'tests/Rec709Native.cpp'),'-o',str(native)])
subprocess.run(command,check=True,cwd=build)
lib=C.CDLL(str(native));D=C.POINTER(C.c_double);F=C.POINTER(C.c_float)
lib.pm_rec709_matrix.argtypes=[D,C.c_int,D];lib.pm_eval30.argtypes=[F,D,C.c_int,F];lib.pm_dctl_eval30.argtypes=[F,D,F];lib.pm_vnext_stages30.argtypes=[D,D,D]
def inv(m):
 a=[list(row)+[Q(i==j) for j in range(3)] for i,row in enumerate(m)]
 for i in range(3):
  k=next(k for k in range(i,3) if a[k][i]);a[i],a[k]=a[k],a[i];v=a[i][i];a[i]=[x/v for x in a[i]]
  for j in range(3):
   if i!=j:
    v=a[j][i];a[j]=[x-v*y for x,y in zip(a[j],a[i])]
 return [row[3:] for row in a]
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(m,v):return [sum(float(m[i][k])*v[k] for k in range(3)) for i in range(3)]
def xyz(xys):
 cols=[[Q(x)/Q(y),Q(1),(1-Q(x)-Q(y))/Q(y)] for x,y in xys];m=list(map(list,zip(*cols)));w=[Q('.3127')/Q('.329'),Q(1),(1-Q('.3127')-Q('.329'))/Q('.329')];scale=[sum(v*w[k] for k,v in enumerate(row)) for row in inv(m)];return [[m[i][j]*scale[j] for j in range(3)] for i in range(3)]
rec=xyz([('.64','.33'),('.30','.60'),('.15','.06')]);dwg=xyz([('.8','.313'),('.1682','.9877'),('.079','-.1155')]);to=mul(inv(dwg),rec);back=mul(inv(rec),dwg)
rng=random.Random(709);pixels=[[0.,0.,0.],[1.,1.,1.],[.18]*3,[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[-.1,.3,2.],[-2.,10.,100.]]+[[rng.uniform(-.2,4) for _ in range(3)] for _ in range(200)]
counts={};errors={}
def check(b,k):counts[k]=counts.get(k,0)+1;assert b,k
def par(**u):
 v={p['id']:p['default'] for p in schema};v.update(u);return (C.c_double*30)(*[v[p['id']] for p in schema])
def eval(lib,x,p):
 o=(C.c_float*4)();lib.pm_eval30((C.c_float*4)(*x,1),p,0,o);return o
for x in pixels:
 for inverse,m in [(0,to),(1,back)]:
  out=(C.c_double*3)();lib.pm_rec709_matrix((C.c_double*3)(*x),inverse,out);e=max(abs(v-w) for v,w in zip(out,mv(m,x)));errors['matrix']=max(errors.get('matrix',0),e);check(e<2e-11*max(1,*map(abs,x)),'independent_matrix')
 out=(C.c_double*3)();lib.pm_rec709_matrix((C.c_double*3)(*x),0,out);rev=(C.c_double*3)();lib.pm_rec709_matrix(out,1,rev);check(max(abs(v-w) for v,w in zip(rev,x))<2e-11*max(1,*map(abs,x)),'active_matrix_roundtrip')
 for it in range(5):
  p=par(pmi_ig=4,pmi_it=it);o=eval(lib,x,p);check(bytes(o)==bytes((C.c_float*4)(*x,1)),'neutral_encoded_bit_exact')
 for density in [-100,0,100]:
  p=par(pmi_ig=4,pmi_it=4,pm_pre=120,pm_compression=40,pm_makeup=150,pm_hue_compression=50,pm_hue_bias=-25,pm_luma_split=100,pm_density=density,pm_chroma=-50)
  o=eval(lib,x,p);inp=[float(C.c_float(v).value) for v in x];st=(C.c_double*17)();lib.pm_vnext_stages30((C.c_double*3)(*mv(to,inp)),p,st);expected=mv(back,list(st[12:15]));e=max(abs(o[i]-expected[i]) for i in range(3));errors['active_same']=max(errors.get('active_same',0),e);check(e<2**-13,'active_same_independent_matrix')
  d=(C.c_float*4)();lib.pm_dctl_eval30((C.c_float*4)(*x,1),p,d);check(bytes(o)==bytes(d),'generated_DCTL_CPU_parity');check(all(math.isfinite(v) for v in o),'finite_active')
if args.legacy_library:
 old=C.CDLL(args.legacy_library);old.pm_eval30.argtypes=[F,D,C.c_int,F]
 for ig in range(4):
  for it in range(5):
   for og in range(5):
    for density in [0,-100,100]:
     p=par(pmi_ig=ig,pmi_it=it,pmi_og=og,pm_makeup=150,pm_hue_bias=-25,pm_luma_split=100,pm_density=density)
     for x in pixels[:12]:check(bytes(eval(old,x,p))==bytes(eval(lib,x,p)),'legacy_profile_bit_exact')
check(schema[0]['options'][4]=='Rec.709 D65' and schema[0]['options'][:4]==['DWG D65','ARRI Wide Gamut 3 D65','ARRI Wide Gamut 4 D65','ACES AP1 CAT02'],'schema_input_append')
check(schema[2]['options'][:5]==['Same as Input','DWG D65','ARRI Wide Gamut 3 D65','ARRI Wide Gamut 4 D65','ACES AP1 CAT02'] and len(schema)==30,'schema_output_count_retained')
report=dict(status='PASS_FOCUSED_REC709',counts=counts,max_errors=errors,legacy_binary_compared=bool(args.legacy_library),native_library_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),legacy_library_sha256=hashlib.sha256(Path(args.legacy_library).read_bytes()).hexdigest() if args.legacy_library else None,limits='Native CPU/generated-DCTL CPU only. Independent rational chromaticity matrices. No Host/CUDA-completed/transfer gamma2.4 or display acceptance.')
(R/'results/v3_curve/REC709.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
