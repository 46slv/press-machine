"""Deterministic HDR cancellation fixtures; standard library only."""
import math
import random
from reference import oracle as o

def extra_pixels():
    center=(1.0182695388793945,1.1546915769577026,-910.28369140625)
    fixtures=[]
    for channel in range(3):
        for offset in range(-128,129):
            rgb=list(center);rgb[channel]=o.from_bits(o.bits(rgb[channel])+offset)
            fixtures.append(tuple(rgb))
    rng=random.Random(120220261110)
    matrix=tuple(zip(*(o.mul(o.XYZ_LMS,o.mul(o.DWG_XYZ,v))
                       for v in ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.)))))
    for row in matrix:
        solved=max(range(3),key=lambda i:abs(row[i]))
        others=[i for i in range(3) if i!=solved]
        for _ in range(10000):
            scale=10**rng.uniform(-5,7)
            linear=[0.,0.,0.]
            for i in others: linear[i]=scale*rng.uniform(-1,1)
            target=scale*rng.choice((-1,0,1))*2**-24
            linear[solved]=(target-math.fsum(row[i]*linear[i] for i in others))/row[solved]
            encoded=tuple(map(o.f32,map(o.encode,linear)))
            if o.encoded_lab(encoded)[0]>.01:fixtures.append(encoded)
    return fixtures
