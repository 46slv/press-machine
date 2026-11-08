from pathlib import Path
import ctypes as c,json,math,struct,random
R=Path(__file__).resolve().parents[1]
schema=json.loads((R.parents[1]/'parameters/press_machine_v2.json').read_text())
default=[p['default'] for p in schema];idx={p['id']:i for i,p in enumerate(schema)}
lib=c.CDLL(str(R/'build/Release/PressMachineParity.dll'))
lib.pm_eval.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.c_int,c.POINTER(c.c_float)]
lib.pm_baseline.argtypes=[c.POINTER(c.c_float),c.POINTER(c.c_double),c.POINTER(c.c_float)]
lib.pm_skin_phase.restype=c.c_double
lib.pm_skin_endpoint.argtypes=[c.c_double,c.c_double,c.c_double,c.c_double,c.c_int,c.POINTER(c.c_double)]
decode=lambda v:v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
linear=[decode(v/255.) for v in (194,150,130)]
srgb_xyz=[[.4123907992659595,.3575843393838780,.1804807884018343],
 [.2126390058715104,.7151686787677559,.0721923153607337],
 [.0193308187155919,.1191947797946260,.9505321522496606]]
xyz=[sum(a*b for a,b in zip(row,linear)) for row in srgb_xyz]
xyz_rec=[[1.7166511879712676,-.35567078377639217,-.2533662813736601],
 [-.6666843518324885,1.6164812366349394,.015768545813911127],
 [.017639857445310936,-.04277061325780865,.9421031212354745]]
rgb=[sum(a*b for a,b in zip(row,xyz)) for row in xyz_rec]
kr,kg,kb=.2627002120112671,.6779980715188708,.05930171646986196
Y=sum(a*b for a,b in zip((kr,kg,kb),rgb))
a=(rgb[0]-Y)/(2*(1-kr));b=(Y-rgb[2])/(2*(1-kb))
phase=math.atan2(b,a);old_phase=.27232316767528086
shift=math.degrees(phase-old_phase)
assert abs(phase-.72821991608931957)<2e-14
assert abs(lib.pm_skin_phase()-phase)<2e-14
endpoint_cases=0;max_axis_error=0.
for points in (1,2,3,4,6):
 for exposure in (-16,-8,0,8,16):
  scale=2.**exposure
  def endpoint(angle):
   o=(c.c_double*2)();lib.pm_skin_endpoint(a*scale,b*scale,Y*scale,angle,points,o);return tuple(o)
  out=endpoint(0);same=endpoint(360)
  assert struct.pack('2d',*out)==struct.pack('2d',*same)
  error=abs(math.remainder(math.atan2(out[1],out[0])-phase,2*math.pi))
  assert error<1e-10,(points,exposure,error)
  max_axis_error=max(max_axis_error,error)
  if points>=2:assert max(abs(out[0]-a*scale),abs(out[1]-b*scale))/scale<1e-10
  endpoint_cases+=1
def state(**kw):
 v=default[:]
 for k,x in kw.items():v[idx[k]]=x
 return v
def evaluate(x,v,old=False):
 src=(c.c_float*4)(*x);values=(c.c_double*25)(*v);out=(c.c_float*4)()
 if old:lib.pm_baseline(src,values,out)
 else:lib.pm_eval(src,values,0,out)
 return tuple(out)
rng=random.Random(194150130)
samples=[(.18,.18,.18,1.),(.4,.2,.1,1.)]+[tuple(rng.uniform(.01,.7) for _ in range(3))+(1.,) for _ in range(8)]
cases=0;max_error=0.;max_relative=0.;changed=0;worst=None
for ig,it in [(0,0),(1,1),(2,2),(3,3),(0,4)]:
 for point_index in range(5):
  for angle in (0.,.1,3.8790404221381,30.,120.,333.8790404221381,360.):
   for amount in (25.,50.,100.):
    v=state(pmi_ig=ig,pmi_it=it,pm_hue_points_index=point_index,pm_hue_angle=angle,pm_hue_compression=amount)
    legacy=v[:];legacy[idx['pm_hue_angle']]=((0. if angle==360. else c.c_float(angle).value)+shift)%360.
    for x in samples:
     new=evaluate(x,v);old=evaluate(x,legacy,True)
     error=max(abs(a-b) for a,b in zip(new[:3],old[:3]))
     relative=error/max(1.,*(abs(q) for q in new[:3]+old[:3]))
     assert relative<=2**-14,(x,v,new,old,relative)
     assert all(math.isfinite(q) for q in new)
     if error>max_error:worst={'profile':[ig,it],'points_index':point_index,'new_angle':angle,'legacy_angle':legacy[idx['pm_hue_angle']],'amount':amount,'input':x,'new':new,'old':old}
     max_error=max(max_error,error);max_relative=max(max_relative,relative);cases+=1
     if angle==0. and new!=evaluate(x,v,True):changed+=1
assert changed>0
result={'status':'PASS','reference':'D65 exact-chromaticity sRGB chart194,150,130; independent double equations',
 'linear_srgb':linear,'XYZ':xyz,'CF2_ab':[a,b],'skin_phase_radians':phase,'phase_shift_degrees':shift,
 'axis_exposure_points_cases':endpoint_cases,'max_axis_error_radians':max_axis_error,
 'legacy_float_translation_cases':cases,'legacy_max_absolute_error':max_error,'legacy_max_normalized_error':max_relative,
 'legacy_normalized_tolerance':2**-14,'worst_legacy_translation_case':worst,'same_angle_intentional_changed_cases':changed,
 'bit_identical_legacy_migration_promised':False,'Host_acceptance':False}
(R/'results/SKIN_AXIS_PHASE.json').write_text(json.dumps(result,indent=2),newline='\n')
print(json.dumps(result,indent=2))
