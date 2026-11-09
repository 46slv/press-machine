from __future__ import annotations
import math,json
from pathlib import Path
PATTERNS={
 "Analogous":[-30.0,0.0,30.0],
 "Complementary":[0.0,180.0],
 "Split Complementary":[0.0,150.0,210.0],
 "Triadic":[0.0,120.0,240.0],
 "Tetradic":[0.0,90.0,180.0,270.0],
}
TAU=2*math.pi
def wrap(x):return (x+math.pi)%TAU-math.pi
def posgap(a,b):
 d=wrap(b-a)
 return d+TAU if d<=0 else d
def F(u,m=.10):return (m*u+(1-m)*(u**3-.5*u**4))/((1+m)/2)
def Q(u):return u*u*(3-2*u)
def target(h,offsets,phi=0.0):
 A=[wrap(phi+math.radians(x)) for x in offsets]
 ds=[wrap(h-a) for a in A];k=min(range(len(A)),key=lambda i:abs(ds[i]));d=ds[k]
 if d>=0:gap=posgap(A[k],A[(k+1)%len(A)])
 else:gap=posgap(A[(k-1)%len(A)],A[k])
 H=.5*gap;u=min(1,max(0,abs(d)/H));ht=A[k]+(1 if d>=0 else -1)*H*F(u);r=1-Q(u)
 return (r*math.cos(ht),r*math.sin(ht))
def qref(y):
 sy=math.sqrt(max(y,0.0));s18=math.sqrt(.18);return (sy-s18)/(sy+s18)
def weight(bias,split,q):
 d=bias/100+split/100*q
 if d==0:return 0.0
 e=2**(2*abs(d));return math.copysign((e-1)/(e+1),d)
order_reversals=0;min_step=1e9;scale_error=0.0;wrap_error=0.0;disp_error=0.0
N=32768
for offsets in PATTERNS.values():
 for phi in (0.0,math.radians(17.3),TAU-1e-10):
  points=[]
  for i in range(N):
   h=-math.pi+TAU*i/N;x,y=target(h,offsets,phi);r=math.hypot(x,y)
   if r>1e-12:points.append((h,math.atan2(y,x),x,y))
  # The target field reaches neutral at cell boundaries. Check local order inside
  # non-neutral runs rather than demanding a hue angle through neutral.
  prev=None
  for h,ho,x,y in points:
   if prev is not None:
    dh=h-prev[0]
    if dh<2.5*TAU/N:
     d=wrap(ho-prev[1])
     if d<-1e-12:order_reversals+=1
     if d>0:min_step=min(min_step,d)
   prev=(h,ho)
  for strength in (0,.25,.5,.75,1):
   for h in (-2.1,-.9,.2,1.4,2.7):
    tx,ty=target(h,offsets,phi);x,y=math.cos(h),math.sin(h)
    ox=x+strength*(tx-x);oy=y+strength*(ty-y)
    full=math.hypot(tx-x,ty-y);got=math.hypot(ox-x,oy-y)
    disp_error=max(disp_error,abs(got-strength*full))
    k=123.456;okx=k*x+strength*(k*tx-k*x);oky=k*y+strength*(k*ty-k*y)
    scale_error=max(scale_error,math.hypot(okx-k*ox,oky-k*oy)/k)
  x0,y0=target(.7,offsets,0.0);x1,y1=target(.7,offsets,TAU)
  wrap_error=max(wrap_error,math.hypot(x0-x1,y0-y1))
us=[i/100000 for i in range(100001)]
curve=[F(u) for u in us]
assert curve[0]==0 and curve[-1]==1 and all(b>a for a,b in zip(curve,curve[1:]))
assert order_reversals==0
assert disp_error<1e-12 and scale_error<1e-12 and wrap_error<1e-12
assert abs(qref(0)+1)<1e-15 and abs(qref(.18))<1e-15
assert abs(qref(.72)-1/3)<1e-15 and abs(qref(2.88)-3/5)<1e-15
grid=[abs(weight(b,s,q)) for b in (-100,-50,0,50,100) for s in (-300,-200,-100,0,100,200,300) for q in (-1,-.5,0,.5,1)]
assert max(grid)<1
receipt={
 "status":"PASS","samples_per_pattern_phase":N,"patterns":list(PATTERNS),
 "analogous_candidates_deg":[30,45,60],"analogous_selected_deg":30,
 "analogous_rationale":"tight 60-degree palette keeps Analogous distinct from Triadic; Primary-Hue dominance remains a separate Hue Bias control",
 "order_reversals":order_reversals,"min_positive_step_rad":min_step,
 "direct_displacement_max_error":disp_error,"scale_covariance_relative_error":scale_error,
 "phase_wrap_error":wrap_error,"combined_extreme_weight":weight(100,300,1),
 "q_ref":{"0":qref(0),".18":qref(.18),".72":qref(.72),"2.88":qref(2.88)}
}
out=Path(__file__).resolve().parent/'REFERENCE_GEOMETRY.json'
out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
