"""75-digit Decimal oracle. No DCTL coefficients, helpers, or emitted matrices.

Primaries from DaVinci Wide Gamut / ARRI WG3 & WG4 / ACES AP1 definitions;
CAT02 Bradford-independent adaptation from ACES D60 to CIE D65. ARRI LogC4
from its spec rational parameters and tangent extension at code zero. No
rounding until the explicit simulated float32 boundary.
"""
from decimal import Decimal as D, getcontext
from functools import lru_cache
getcontext().prec = 75

def dot(row,v):
    return sum(a*b for a,b in zip(row,v))

def mv(m,v):
    return tuple(dot(row,v) for row in m)

def mm(a,b):
    return tuple(tuple(dot(row,col) for col in zip(*b)) for row in a)

def inv(m):
    a=[list(r)+[D(j==i) for j in range(3)] for i,r in enumerate(m)]
    for i in range(3):
        k=max(range(i,3),key=lambda k: abs(a[k][i])); a[k],a[i]=a[i],a[k]
        a[i]=[x/a[i][i] for x in a[i]]
        for k in range(3):
            if k!=i:
                c=a[k][i]; a[k]=[x-c*y for x,y in zip(a[k],a[i])]
    return tuple(tuple(r[3:]) for r in a)

def xyz(x,y):
    x,y=D(x),D(y)
    return (x/y,D(1),(1-x-y)/y)

D65=xyz('.3127','.3290'); D60=xyz('.32168','.33767')
CAT=tuple(tuple(map(D,r.split())) for r in (
    '.7328 .4296 -.1624', '-.7036 1.6975 .0061', '.0030 .0136 .9834'))

def diag(s):
    return tuple(tuple(x if i==j else D(0) for j in range(3)) for i,x in enumerate(s))

def primaries(xys,white):
    unscaled=tuple(zip(*(xyz(*p.split()) for p in xys)))
    return mm(unscaled,diag(mv(inv(unscaled),white)))

BASES=[primaries(p.split(';'),D65) for p in (
    '.8000 .3130;.1682 .9877;.0790 -.1155',
    '.6840 .3130;.2210 .8480;.0861 -.1020',
    '.7347 .2653;.1424 .8576;.0991 -.0308')]
BASES.append(mm(mm(inv(CAT),mm(diag(tuple(a/b for a,b in zip(mv(CAT,D65),mv(CAT,D60)))),CAT)),
    primaries('.713 .293;.165 .830;.128 .044'.split(';'),D60)))

@lru_cache(None)
def matrix(ig,og):
    return diag((D(1),)*3) if ig==og else mm(inv(BASES[og]),BASES[ig])

LN2=D(2).ln(); LN10=D(10).ln()
A=(2**18-D(16))/D('117.45')
B=D(928)/1023; C=1-B
E=D(2)**(6-14*C/B)
T=(E-64)/A
S=14*LN2*E/(A*B)

@lru_cache(65536)
def decode(v,t):
    x=D(v)
    if t==4: return x
    if t==2: return T+S*x if x<0 else (D(2)**(6+14*(x-C)/B)-64)/A
    if t==0:
        return x/D('10.44426855') if x<=D('.02740668') else D(2)**(x/D('.07329248')-7)-D('.0075')
    if t==1:
        a,b,c,d,e,f=map(D,'5.555556 .052272 .247190 .385537 5.367655 .092809'.split())
        return (x-f)/e if x<=e*D('.010591')+f else (D(10)**((x-d)/c)-b)/a
    return (x-D('.0729055341958355'))/D('10.5402377416545') if x<=D('.155251141552511') else D(2)**(D('17.52')*x-D('9.72'))

@lru_cache(65536)
def encode(v,t):
    x=D(v)
    if t==4: return x
    if t==2: return (x-T)/S if x<T else ((A*x+64).ln()/LN2-6)*B/14+C
    if t==0:
        return x*D('10.44426855') if x<=D('.00262409') else ((x+D('.0075')).ln()/LN2+7)*D('.07329248')
    if t==1:
        a,b,c,d,e,f=map(D,'5.555556 .052272 .247190 .385537 5.367655 .092809'.split())
        return e*x+f if x<=D('.010591') else c*(a*x+b).ln()/LN10+d
    return D('10.5402377416545')*x+D('.0729055341958355') if x<=D('.0078125') else (x.ln()/LN2+D('9.72'))/D('17.52')

def convert(rgb,ig,it,og,ot):
    return tuple(encode(v,ot) for v in mv(matrix(ig,og),tuple(decode(x,it) for x in rgb)))
