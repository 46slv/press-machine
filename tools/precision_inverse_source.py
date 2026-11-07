"""Generate the same color model end to end in compensated binary32 pairs.

Constants are copied independently from the published DWG/DI and W3C tables.
This module deliberately does not import the independent reference oracle.
"""
DWG_XYZ = (
    ('.70062239', '.14877482', '.10105872'),
    ('.27411851', '.87363190', '-.14775041'),
    ('-.09896291', '-.13789533', '1.32591599'))
XYZ_LMS = (
    ('.8190224379967030', '.3619062600528904', '-.1288737815209879'),
    ('.0329836539323885', '.9292868615863434', '.0361446663506424'),
    ('.0481771893596242', '.2642395317527308', '.6335478284694309'))
ROOT_LAB = (
    ('.2104542683093140', '.7936177747023054', '-.0040720430116193'),
    ('1.9779985324311684', '-2.4285922420485799', '.4505937096174110'),
    ('.0259040424655478', '.7827717124575296', '-.8086757549230774'))
LAB_ROOT = (
    ('1', '.3963377773761749', '.2158037573099136'),
    ('1', '-.1055613458156586', '-.0638541728258133'),
    ('1', '-.0894841775298119', '-1.2914855480194092'))
LMS_XYZ = (
    ('1.2268798758459243', '-.5578149944602171', '.2813910456659647'),
    ('-.0405757452148008', '1.1122868032803170', '-.0717110580655164'),
    ('-.0763729366746601', '-.4214933324022432', '1.5869240198367816'))
XYZ_DWG = (
    ('1.51667204', '-.28147805', '-.14696363'),
    ('-.46491710', '1.25142378', '.17488461'),
    ('.06484905', '.10913934', '.76141462'))

HELPERS = r'''
// Keep residuals through the entire ill-conditioned path: prematurely rounding
// Lab, S or the inverse basis can amplify one ulp during HDR cancellation.
__DEVICE__ float2 pm_pair_cbrt(float2 v) {
    // Exact power-of-two range reduction keeps root^3 residuals finite
    // even when a rounded cube-root seed lies just above cbrt(FLT_MAX).
    float factor=1.0f;
    if (_fabs(v.x)>4.0e37f) { v=pm_pair_mul(v,pm_pair(0.125f)); factor=2.0f; }
    float h=pm_cbrt(v.x);
    if (h==0.0f) return pm_pair(h);
    float2 root=pm_pair(h);
    for (int i=0;i<2;i++) {
        float2 square=pm_pair_mul(root,root);
        float2 residual=pm_pair_add(v,pm_pair_neg(pm_pair_mul(square,root)));
        root=pm_pair_add(root,pm_pair_div(residual,pm_pair_mul(pm_pair(3.0f),square)));
    }
    return pm_pair_mul(root,pm_pair(factor));
}
__DEVICE__ float2 pm_pair_sqrt(float2 v) {
    float h=_sqrtf(v.x);
    if (h==0.0f) return pm_pair(h);
    float2 root=pm_pair(h);
    float2 residual=pm_pair_add(v,pm_pair_neg(pm_pair_mul(root,root)));
    return pm_pair_add(root,pm_pair_div(residual,pm_pair_mul(pm_pair(2.0f),root)));
}
__DEVICE__ float2 pm_precise_transfer(float2 s,float t,float compression,float softness) {
    float2 hundred=pm_pair(100.0f);
    float2 a=pm_pair_div(pm_pair(compression),hundred);
    float2 q=pm_pair_div(pm_pair_add(hundred,pm_pair(-compression)),hundred);
    float2 half=pm_pair_mul(pm_pair(t),pm_pair_div(pm_pair(softness),hundred));
    float2 lo=pm_pair_add(pm_pair(t),pm_pair_neg(half));
    float2 hi=pm_pair_add(pm_pair(t),half);
    float2 x=pm_pair_add(s,pm_pair_neg(lo));
    if (x.x<0.0f || (x.x==0.0f && x.y<=0.0f)) return s;
    float2 upper=pm_pair_add(s,pm_pair_neg(hi));
    if (half.x==0.0f || upper.x>0.0f || (upper.x==0.0f && upper.y>=0.0f)) {
        return pm_pair_add(pm_pair(t),pm_pair_mul(q,pm_pair_add(s,pm_pair(-t))));
    }
    float2 numerator=pm_pair_mul(a,pm_pair_mul(x,x));
    float2 denominator=pm_pair_mul(pm_pair(4.0f),half);
    return pm_pair_add(s,pm_pair_neg(pm_pair_div(numerator,denominator)));
}
__DEVICE__ int pm_precision_route(float3 lms) {
    float largest=_fmaxf(_fabs(lms.x),_fmaxf(_fabs(lms.y),_fabs(lms.z)));
    float region=largest*0.00390625f;
    return _fabs(lms.x)<=region || _fabs(lms.y)<=region || _fabs(lms.z)<=region;
}
'''

def augment(base, pair):
    def matrix(table, first=False):
        out='' if first else '    x=a; y=b; z=c;\n'
        for name, row in zip(('a', 'b', 'c'), table):
            dot='pm_precise_dot3(x,y,z,'+','.join(pair(v) for v in row)+')'
            out+='    '+('float2 ' if first else '')+name+'='+dot+';\n'
        return out

    helper=HELPERS+'''
__DEVICE__ float3 pm_precise_transform(float3 original) {
    float2 x=pm_precise_decode(original.x);
    float2 y=pm_precise_decode(original.y);
    float2 z=pm_precise_decode(original.z);
'''
    helper+=matrix(DWG_XYZ, first=True)
    helper+=matrix(XYZ_LMS)
    helper+='    a=pm_pair_cbrt(a); b=pm_pair_cbrt(b); c=pm_pair_cbrt(c);\n'
    helper+=matrix(ROOT_LAB)
    helper+='''
    float3 lab=make_float3(a.x,b.x,c.x);
    float2 chroma=pm_pair_sqrt(pm_pair_add(pm_pair_mul(b,b),pm_pair_mul(c,c)));
    if (!pm_finite3(lab) || !pm_finite(chroma.x) || lab.x<=1.0e-6f || chroma.x<=1.0e-7f) return original;
    float2 sat=pm_pair_mul(pm_pair(100.0f),pm_pair_div(chroma,a));
    if (!pm_finite(sat.x) || sat.x<=1.0e-7f) return original;
    float2 out_sat=pm_precise_transfer(sat,pm_threshold,pm_compression,pm_softness);
    if (!pm_finite(out_sat.x)) return original;
    if (out_sat.x==sat.x && out_sat.y==sat.y) return original;
    float2 scale=pm_pair_div(out_sat,sat);
    b=pm_pair_mul(b,scale); c=pm_pair_mul(c,scale);
'''
    helper+=matrix(LAB_ROOT)
    for name in ('a','b','c'):
        helper+='    '+name+'=pm_pair_mul('+name+',pm_pair_mul('+name+','+name+'));\n'
    helper+=matrix(LMS_XYZ)
    helper+=matrix(XYZ_DWG)
    helper+='''
    float3 linear=make_float3(pm_rn_add(a.x,a.y),pm_rn_add(b.x,b.y),pm_rn_add(c.x,c.y));
    if (!pm_finite3(linear)) return original;
    float3 encoded=make_float3(pm_encode(linear.x),pm_encode(linear.y),pm_encode(linear.z));
    return pm_finite3(encoded) ? encoded : original;
}
'''
    at=base.index('__DEVICE__ int pm_domain')
    base=base[:at]+helper+base[at:]
    old='    lms=pm_condition_lms(original,lms);'
    assert base.count(old)==1
    return base.replace(old,'    if (pm_precision_route(lms)) return pm_precise_transform(original);')
