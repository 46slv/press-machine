"""Independent double-precision DEV-12 R2 oracle; no DCTL imports or parsing.

Matrix data: Blackmagic DWG/DI v1.1 and W3C CSS Color 4 (2026-11-03).
Only Python's standard library is required. See docs/CONTRACT.md.
"""
import math
import struct
from dataclasses import dataclass

F32_MAX = float.fromhex('0x1.fffffep+127')
DWG_XYZ = ((.70062239, .14877482, .10105872),
           (.27411851, .87363190, -.14775041),
           (-.09896291, -.13789533, 1.32591599))
XYZ_DWG = ((1.51667204, -.28147805, -.14696363),
           (-.46491710, 1.25142378, .17488461),
           (.06484905, .10913934, .76141462))
XYZ_LMS = ((.8190224379967030, .3619062600528904, -.1288737815209879),
           (.0329836539323885, .9292868615863434, .0361446663506424),
           (.0481771893596242, .2642395317527308, .6335478284694309))
ROOT_LAB = ((.2104542683093140, .7936177747023054, -.0040720430116193),
            (1.9779985324311684, -2.4285922420485799, .4505937096174110),
            (.0259040424655478, .7827717124575296, -.8086757549230774))
LAB_ROOT = ((1., .3963377773761749, .2158037573099136),
            (1., -.1055613458156586, -.0638541728258133),
            (1., -.0894841775298119, -1.2914855480194092))
LMS_XYZ = ((1.2268798758459243, -.5578149944602171, .2813910456659647),
           (-.0405757452148008, 1.1122868032803170, -.0717110580655164),
           (-.0763729366746601, -.4214933324022432, 1.5869240198367816))

def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]

def bits(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]

def from_bits(x):
    return struct.unpack('<f', struct.pack('<I', x))[0]

def mul(matrix, vector):
    return tuple(math.fsum(a*b for a, b in zip(row, vector)) for row in matrix)

def encode(x):
    return x*10.44426855 if x <= .00262409 else (math.log2(x+.0075)+7)*.07329248

def decode(x):
    return x/10.44426855 if x <= .02740668 else 2**(x/.07329248-7)-.0075

def xyz_lab(xyz):
    return mul(ROOT_LAB, tuple(math.cbrt(x) for x in mul(XYZ_LMS, xyz)))

def lab_xyz(lab):
    return mul(LMS_XYZ, tuple(x**3 for x in mul(LAB_ROOT, lab)))

def linear_lab(rgb):
    return xyz_lab(mul(DWG_XYZ, rgb))

def lab_linear(lab):
    return mul(XYZ_DWG, lab_xyz(lab))

def encoded_lab(rgb):
    return linear_lab(tuple(decode(x) for x in rgb))

def lab_encoded(lab):
    return tuple(encode(x) for x in lab_linear(lab))

def saturation(lab):
    return 100*math.hypot(*lab[1:])/lab[0]

def transfer(s, threshold=25., compression=0., softness=20.):
    """Published scalar law. Parameters are valid UI-domain values, no clamps."""
    if compression == 0:
        return s
    strength = compression/100
    width = 2*threshold*softness/100
    lower = threshold*(1-softness/100)
    upper = threshold*(1+softness/100)
    if width and lower < s < upper:
        return s - strength*(s-lower)**2/(2*width)
    if s <= (lower if width else threshold):
        return s
    return threshold + (1-strength)*(s-threshold)

def valid_domain(lab, chroma, s):
    return (all(math.isfinite(x) for x in (*lab, chroma, s)) and
            lab[0] > 1e-6 and chroma > 1e-7 and s > 1e-7)

@dataclass(frozen=True)
class Result:
    rgb: tuple
    path: str
    s_in: float = 0.
    s_out: float = 0.

def _stage(v):
    # The target uses float32. Reject unrepresentable intermediates rather than
    # substituting an artistic ceiling/clamp. This oracle still computes in double.
    if not all(math.isfinite(x) and abs(x) <= F32_MAX for x in v):
        raise ArithmeticError('unrepresentable float32 intermediate')
    return v

def apply(rgb, threshold=25., compression=0., softness=20., bypass=False):
    original = tuple(rgb)
    if bypass or compression == 0:
        return Result(original, 'control_identity')
    if not all(math.isfinite(x) for x in rgb):
        return Result(original, 'nonfinite_input')
    if rgb[0] == rgb[1] == rgb[2]:
        return Result(original, 'neutral')
    try:
        linear = _stage(tuple(decode(x) for x in rgb))
        xyz = _stage(mul(DWG_XYZ, linear))
        lms = _stage(mul(XYZ_LMS, xyz))
        lab = _stage(mul(ROOT_LAB, tuple(math.cbrt(x) for x in lms)))
        chroma = math.hypot(*lab[1:])
        if lab[0] <= 1e-6 or chroma <= 1e-7:
            return Result(original, 'domain_identity')
        s = 100*chroma/lab[0]
        if not valid_domain(lab, chroma, s) or abs(s) > F32_MAX:
            return Result(original, 'domain_identity')
        out_s = transfer(s, threshold, compression, softness)
        if out_s == s:
            return Result(original, 'untouched', s, out_s)
        out_lab = (lab[0], *(x*out_s/s for x in lab[1:]))
        root = _stage(mul(LAB_ROOT, out_lab))
        lms = _stage(tuple(x**3 for x in root))
        xyz = _stage(mul(LMS_XYZ, lms))
        linear = _stage(mul(XYZ_DWG, xyz))
        out = _stage(tuple(encode(x) for x in linear))
        return Result(out, 'compressed', s, out_s)
    except (OverflowError, ValueError, ArithmeticError):
        return Result(original, 'range_identity')
