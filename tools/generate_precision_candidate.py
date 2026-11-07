"""Generate an isolated, algebraically unchanged R2 precision candidate.

Constants are split from Decimal reference values, not rounded float literals.
No installed or approved product source is written by this tool.
"""
from decimal import Decimal, localcontext
from pathlib import Path
import math
import struct
import argparse
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
def pair(value):
    value=Decimal(value)
    high=struct.unpack('<f',struct.pack('<f',float(value)))[0]
    low=struct.unpack('<f',struct.pack('<f',float(value-Decimal.from_float(high))))[0]
    def literal(x):
        out=repr(x)
        return out+'f' if '.' in out or 'e' in out else out+'.0f'
    return 'make_float2('+literal(high)+', '+literal(low)+')'

def dot(row):
    return 'pm_precise_dot3(x,y,z,'+','.join(pair(c) for c in row)+')'

BASE_COMMIT='7e48d7b1ac55eac23739d0a1f620b35779aa7a40'
def generate_source():
    base=subprocess.check_output(['git','-C',str(ROOT),'show',
        BASE_COMMIT+':dctl/PressMachine_R2.dctl']).decode('utf-8')
    begin=base.index('// Compensated binary32 pairs')
    end=base.index('__DEVICE__ float pm_transfer',begin)
    from tools.rounded_pair_source import RN_PAIR_SOURCE
    pairs=RN_PAIR_SOURCE.lstrip("\n")
    base=base[:begin]+base[end:]
    at=base.index('__DEVICE__ float pm_decode')
    base=base[:at]+pairs+base[at:]
    helper='''// Precision fallback only: the ordinary binary32 path loses the sign/magnitude
// of nearly cancelling LMS sums. Re-evaluate the SAME DI and published matrices
// in float pairs when an LMS component loses at least eight relative bits.
// No epsilon guard, chroma curve, lightness, hue or output weighting is changed.
__DEVICE__ float2 pm_precise_dot3(float2 x,float2 y,float2 z,
                                  float2 a,float2 b,float2 c) {
    return pm_pair_add(pm_pair_add(pm_pair_mul(a,x),pm_pair_mul(b,y)),pm_pair_mul(c,z));
}
__DEVICE__ float2 pm_precise_decode(float v) {
'''
    helper+='    if (v <= 0.02740668f) return pm_pair_div(pm_pair(v),'+pair('10.44426855')+');\n'
    helper+='    float2 exponent = pm_pair_add(pm_pair_div(pm_pair(v),'+pair('.07329248')+'),pm_pair(-7.0f));\n'
    helper+='''    // Finite decoded values in the log branch have integer exponent >= -7.
    // Existing fast-path range handling owns unrepresentable large values.
    if (exponent.x > 127.0f) return pm_pair(pm_decode(v));
    float n = _floorf(exponent.x);
    if (exponent.x == n && exponent.y < 0.0f) n -= 1.0f;
    float2 r = pm_pair_add(exponent,pm_pair(-n));
    // Degree-16 Taylor polynomial for 2^r, 0 <= r <= 1. Its analytic
    // truncation bound is 2*ln(2)^17/17! < 1.4e-17 before pair rounding.
'''
    with localcontext() as context:
        context.prec=80
        ln2=Decimal(2).ln()
        coeff=[ln2**k/Decimal(math.factorial(k)) for k in range(17)]
        helper+='    float2 y = '+pair(coeff[-1])+';\n'
        for c in reversed(coeff[:-1]):
            helper+='    y = pm_pair_add(pm_pair_mul(y,r),'+pair(c)+');\n'
    helper+='    return pm_pair_add(pm_pair_mul(y,pm_pair(_powf(2.0f,n))),pm_pair_neg('+pair('.0075')+'));\n}\n'
    helper+='''__DEVICE__ float3 pm_precise_lms(float3 encoded) {
    float2 x=pm_precise_decode(encoded.x);
    float2 y=pm_precise_decode(encoded.y);
    float2 z=pm_precise_decode(encoded.z);
'''
    dwg=[['.70062239','.14877482','.10105872'],
         ['.27411851','.87363190','-.14775041'],
         ['-.09896291','-.13789533','1.32591599']]
    lms=[['.8190224379967030','.3619062600528904','-.1288737815209879'],
         ['.0329836539323885','.9292868615863434','.0361446663506424'],
         ['.0481771893596242','.2642395317527308','.6335478284694309']]
    for name,row in zip(('a','b','c'),dwg):
        helper+='    float2 '+name+' = '+dot(row)+';\n'
    helper+='    x=a; y=b; z=c;\n'
    for name,row in zip(('a','b','c'),lms):
        helper+='    '+name+' = '+dot(row)+';\n'
    helper+='    return make_float3(a.x+a.y,b.x+b.y,c.x+c.y);\n}\n'
    helper+='''__DEVICE__ float3 pm_condition_lms(float3 encoded,float3 lms) {
    float largest = _fmaxf(_fabs(lms.x),_fmaxf(_fabs(lms.y),_fabs(lms.z)));
    float error_region = largest*0.00390625f; // 2^-8, precision routing only.
    if (_fabs(lms.x)<=error_region || _fabs(lms.y)<=error_region || _fabs(lms.z)<=error_region) {
        float3 precise=pm_precise_lms(encoded);
        if (pm_finite3(precise)) return precise;
    }
    return lms;
}
'''
    at=base.index('__DEVICE__ int pm_domain')
    base=base[:at]+helper+base[at:]
    needle='    if (!pm_finite3(lms)) return original;\n    float3 lab'
    assert base.count(needle)==1
    base=base.replace(needle,'    if (!pm_finite3(lms)) return original;\n    lms=pm_condition_lms(original,lms);\n    float3 lab')
    base=base.replace('return out.x + out.y;','return pm_rn_add(out.x,out.y);')
    base=base.replace('make_float3(a.x+a.y,b.x+b.y,c.x+c.y)','make_float3(pm_rn_add(a.x,a.y),pm_rn_add(b.x,b.y),pm_rn_add(c.x,c.y))')
    endpoint = '''    if (compression == 0.0f) return s;
#ifdef DEVICE_IS_CUDA
    // This exact published endpoint is zero for every finite positive S.
    // Integer classification avoids fast-math comparisons treating a positive
    // subnormal S as zero and incorrectly returning it unchanged.
    int s_word=__float_as_int(s);
    if ((__float_as_int(t) & 0x7fffffff)==0 && compression==100.0f && s_word>0 && s_word<0x7f800000) return 0.0f;
#endif'''
    old_endpoint='    if (compression == 0.0f) return s;'
    assert base.count(old_endpoint)==1
    base=base.replace(old_endpoint,endpoint)
    root = '    return x < 0.0f ? -_powf(-x, 1.0f / 3.0f) : _powf(x, 1.0f / 3.0f);'
    assert base.count(root)==1
    base=base.replace(root,'#ifdef DEVICE_IS_CUDA\n    return cbrtf(x);\n#else\n'+root+'\n#endif')
    from tools.precision_inverse_source import augment
    return augment(base,pair)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.write_text(generate_source(),encoding='utf-8',newline='\n')
    print(args.output)
