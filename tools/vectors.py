"""Deterministic float-boundary vectors. No DCTL code is used for expectations."""
import itertools
import json
import math
from pathlib import Path
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference import oracle as o

STATES = {'bypass': (25.,75.,20.,True), 'zero': (25.,0.,20.,False),
          'moderate': (25.,50.,20.,False), 'strong': (25.,100.,100.,False),
          'hard_zero': (0.,75.,0.,False), 'untouched': (200.,75.,20.,False)}

def colors():
    values = []
    def add(name, rgb):
        values.append((name, tuple(o.f32(x) for x in rgb)))
    for x in (-1., -0., 0., .02740668, .336043, 1., 1.2):
        add('neutral_'+str(x), (x,)*3)
    for name, rgb in [('warm',(.6,.2,.08)), ('red',(1.,.001,.001)),
                      ('blue',(.001,.001,1.)), ('cyan',(.001,.5,.5)),
                      ('negative_lms',(-.2,.05,.5)), ('mixed',(-.04,.3,1.2)),
                      ('hdr',(1000.,2.,.1)), ('dark_red',(1e-9,1e-12,1e-12))]:
        add(name, tuple(o.encode(x) for x in rgb))
    for power in (-8,0,8):
        add('exposure_'+str(power), tuple(o.encode(x*2**power) for x in (.8,.08,.01)))
    for l in (0.999e-6, 1e-6, 1.001e-6):
        add('L_guard_'+str(l), o.lab_encoded((l, 2e-7, 0.)))
    for c in (.5e-7, .999e-7, 1e-7, 1.001e-7, 2e-7):
        add('C_guard_'+str(c), o.lab_encoded((.001,c,0.)))
    # Scalars near all three knee positions, in several hue directions.
    for s,h in itertools.product((19.999,20.,20.001,25.,29.999,30.,30.001,150.,250.), (0.,2.,4.)):
        c=.5*s/100
        add(f'S{s}_h{h}', o.lab_encoded((.5,c*math.cos(h),c*math.sin(h))))
    # Full finite-boundary protection samples, not representative grading colors.
    add('decode_overflow', (o.F32_MAX,0.,.25))
    add('huge_negative', (-o.F32_MAX,-o.F32_MAX/2,-o.F32_MAX/4))
    add('subnormal', (o.from_bits(1),o.from_bits(2),-o.from_bits(1)))
    return values

def pixels():
    for name,rgb in colors():
        for state,(t,c,p,b) in STATES.items():
            yield {'id':name+'/'+state, 'rgb':rgb, 'params':[t,c,p,b], 'group':'contract'}

def scalar_cases():
    for t,c,p in itertools.product((0.,25.,100.),(0.,25.,50.,75.,100.),(0.,20.,100.)):
        lo,hi=t*(1-p/100),t*(1+p/100)
        points={0.,1e-7,500.,1000.}
        for q in (lo,t,hi):
            w=o.bits(q)
            points.update(o.from_bits(i) for i in (max(0,w-1),w,w+1))
        # Ordered dense grid plus immediate float neighbors of boundaries.
        points.update(i/8 for i in range(4001))
        for s in sorted(points):
            yield (o.f32(s),t,c,p)

def domain_cases():
    for l,c in itertools.product((.999e-6,1e-6,1.001e-6,.5),(.999e-7,1e-7,1.001e-7,.2)):
        yield tuple(o.f32(x) for x in (l,c,0.))

def finite_stress():
    rng=random.Random(120220261105)
    for i in range(256):
        words=[rng.randrange(0xff000000) for _ in range(3)]
        rgb=tuple(o.from_bits(w) for w in words)
        if all(math.isfinite(x) for x in rgb):
            yield {'id':f'finite_bits_{i}', 'rgb':rgb,'params':[25.,75.,20.,False], 'group':'finite_only'}

def write():
    path=Path(__file__).resolve().parents[1]/'fixtures/vectors.jsonl'
    path.parent.mkdir(exist_ok=True)
    rows=[]
    for v in [*pixels(),*finite_stress()]:
        expected=o.apply(v['rgb'],*v['params'])
        rows.append(json.dumps({**v,'rgb_bits':[o.bits(x) for x in v['rgb']],
                               'expected':expected.__dict__},sort_keys=True))
    path.write_text('\n'.join(rows)+'\n',encoding='utf-8',newline='\n')
    return path

if __name__ == '__main__':
    print(write())
