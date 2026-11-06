"""Independent double model of a proposed continuous signed-L domain revision.

This proposal is NOT the approved R2 contract. S=100*C/abs(L) for L != 0;
L=0 uses its infinite-S limit. Original matrices and signed L/hue are retained.
"""
import math
from reference import oracle as o


def chroma_out(lightness, chroma, threshold, compression, softness):
    if compression == 0:
        return chroma
    magnitude = abs(lightness)
    if magnitude == 0:
        return chroma*(1-compression/100)
    s = 100*chroma/magnitude
    return chroma*o.transfer(s,threshold,compression,softness)/s


def apply(rgb, threshold=25., compression=0., softness=20., bypass=False):
    original=tuple(rgb)
    if bypass or compression == 0:
        return o.Result(original,'control_identity')
    if not all(math.isfinite(x) for x in original):
        return o.Result(original,'nonfinite_input')
    if original[0] == original[1] == original[2]:
        return o.Result(original,'neutral')
    try:
        linear=o._stage(tuple(o.decode(x) for x in original))
        xyz=o._stage(o.mul(o.DWG_XYZ,linear))
        lms=o._stage(o.mul(o.XYZ_LMS,xyz))
        lab=o._stage(o.mul(o.ROOT_LAB,tuple(math.cbrt(x) for x in lms)))
        c=math.hypot(*lab[1:])
        if c <= 1e-7:
            return o.Result(original,'chroma_identity')
        out_c=chroma_out(lab[0],c,threshold,compression,softness)
        if out_c == c:
            return o.Result(original,'untouched')
        out_lab=(lab[0],lab[1]*out_c/c,lab[2]*out_c/c)
        root=o._stage(o.mul(o.LAB_ROOT,out_lab))
        lms=o._stage(tuple(x**3 for x in root))
        xyz=o._stage(o.mul(o.LMS_XYZ,lms))
        linear=o._stage(o.mul(o.XYZ_DWG,xyz))
        out=o._stage(tuple(o.encode(x) for x in linear))
        return o.Result(out,'compressed')
    except (OverflowError,ValueError,ArithmeticError):
        return o.Result(original,'range_identity')
