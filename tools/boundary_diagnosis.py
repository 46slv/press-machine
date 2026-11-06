"""Separate the recorded Oklab cusp from numerical error and the R2 L guard.

Read-only with respect to product sources and host state. Uses actual DCTL
native binaries plus independent double reference. No color-model repair.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference import oracle as o
from reference import continuous_oracle as co
from tools import domain_probe as d

ROOT = Path(__file__).resolve().parents[1]
PARAMS = (25., 75., 20., False)


def linear_at(u, peak=1.):
    return (peak*.18*(1-u), peak*.18*(1-u),
            peak*(.18*(1-u)+u))


def lms_at(u):
    return o.mul(o.XYZ_LMS, o.mul(o.DWG_XYZ, linear_at(u)))


def zero_crossing():
    a, b = lms_at(0.), lms_at(1.)
    roots = [(i, -x/(y-x)) for i, (x, y) in enumerate(zip(a, b))
             if x*y < 0.]
    return min(roots, key=lambda row: abs(row[1]*1023-572.5))


def linear_output(u, compression=75., continuous=False):
    rgb = linear_at(u)
    lab = o.linear_lab(rgb)
    c = math.hypot(*lab[1:])
    if continuous:
        out_c = co.chroma_out(lab[0], c, 25., compression, 20.)
    else:
        if lab[0] <= 1e-6:
            return rgb
        s = 100*c/lab[0]
        out_c = c*o.transfer(s, 25., compression, 20.)/s
    return o.lab_linear((lab[0], lab[1]*out_c/c, lab[2]*out_c/c))


def maximum_delta(a, b):
    return max(abs(x-y) for x, y in zip(a, b))


def recorded_pair():
    inputs = [tuple(map(o.f32, map(o.encode, linear_at(i/1023))))
              for i in (572, 573)]
    req = [('P', rgb, PARAMS) for rgb in inputs]
    native = d.native(req, d.EXE)
    proposal = d.native(req)
    reference = [o.apply(rgb, *PARAMS).rgb for rgb in inputs]
    output = {'offsets':[572,573], 'controls':PARAMS,
              'linear_inputs':[linear_at(i/1023) for i in (572,573)],
              'encoded_float_inputs':inputs,
              'LMS_from_encoded_input':[o.mul(o.XYZ_LMS,o.mul(o.DWG_XYZ,
                 tuple(map(o.decode,rgb)))) for rgb in inputs],
              'Lab_from_encoded_input':[o.encoded_lab(rgb) for rgb in inputs],
              'native_linear':[tuple(map(o.decode,rgb)) for rgb in native],
              'oracle_linear':[tuple(map(o.decode,rgb)) for rgb in reference],
              'proposal_linear':[tuple(map(o.decode,rgb)) for rgb in proposal],
              'max_encoded_native_oracle_error':max(maximum_delta(a,b)
                 for a,b in zip(native,reference))}
    output['native_blue_delta']=output['native_linear'][1][2]-output['native_linear'][0][2]
    output['oracle_blue_delta']=output['oracle_linear'][1][2]-output['oracle_linear'][0][2]
    return output


def convergence():
    component, u0 = zero_crossing()
    rows = []
    for exponent in range(10, 33, 2):
        h = 2.**-exponent
        left, right = linear_output(u0-h), linear_output(u0+h)
        rows.append({'half_width_u':h,'width_in_original_pixels':2*h*1023,
                     'left_L':o.linear_lab(linear_at(u0-h))[0],
                     'right_L':o.linear_lab(linear_at(u0+h))[0],
                     'max_channel_delta':maximum_delta(left,right),
                     'blue_delta':right[2]-left[2]})
    for previous, row in zip(rows, rows[1:]):
        row['ratio_to_previous_delta']=row['max_channel_delta']/previous['max_channel_delta']
    return {'LMS_component':component,'crossing_u':u0,
            'crossing_offset':u0*1023,'crossing_LMS':lms_at(u0),
            'crossing_L':o.linear_lab(linear_at(u0))[0],
            'expected_cuberoot_ratio_for_four_times_smaller_width':4**(-1/3),
            'rows':rows}


def focused_numeric():
    _, u0=zero_crossing()
    # The exact encoded input is shared by oracle and native. This does not
    # compare binary32 output against unquantized source pixels.
    requests=[]; fixtures=[]
    for peak in (.01,.1,1.,4.):
        for i in range(2049):
            u=u0+(i-1024)/(1024*1023)
            rgb=tuple(map(o.f32,map(o.encode,linear_at(u,peak))))
            fixtures.append((peak,u,rgb))
            requests.append(('P',rgb,PARAMS))
    actual=d.native(requests,d.EXE)
    worst={'normalized_error':0.}
    over=0
    for fixture,value in zip(fixtures,actual):
        peak,u,rgb=fixture
        expected=o.apply(rgb,*PARAMS)
        error=maximum_delta(value,expected.rgb)/max(1.,*map(abs,expected.rgb))
        if error>2**-13: over+=1
        if error>worst['normalized_error']:
            lms=o.mul(o.XYZ_LMS,o.mul(o.DWG_XYZ,tuple(map(o.decode,rgb))))
            worst={'normalized_error':error,'peak':peak,'offset':u*1023,
                   'input_encoded':rgb,'input_LMS':lms,
                   'native_encoded':value,'oracle_encoded':expected.rgb,
                   'oracle_path':expected.path}
    return {'samples':len(fixtures),
            'reference':'same binary32 encoded input, independent double arithmetic',
            'existing_empirical_RGB_envelope':2**-13,
            'outside_existing_empirical_envelope':over,'worst':worst}


def measure():
    return {'status':'DIAGNOSTIC_NOT_ACCEPTANCE_OR_PRODUCT_REVISION',
            'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (ROOT/'dctl/PressMachine_R2.dctl',
                           ROOT/'prototypes/PressMachine_ContinuousDomain.dctl',
                           ROOT/'reference/oracle.py')},
            'recorded_LMS_pair':recorded_pair(),
            'double_precision_convergence':convergence(),
            'focused_native_precision':focused_numeric(),
            'host_state':'UNTOUCHED','product_source':'READ_ONLY_BY_THIS_DIAGNOSTIC',
            'new_Resolve_validation':'NOT_RUN','user_visual_acceptance':'NOT_RUN'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    compiler=d.build_both()
    result=measure()
    result['compiler']=compiler
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='compiler'},indent=2))


if __name__=='__main__':
    main()

def cancellation_planes():
    import random
    rng=random.Random(120220261109)
    matrix=tuple(zip(*(o.mul(o.XYZ_LMS,o.mul(o.DWG_XYZ,v))
                       for v in ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.)))))
    fixtures=[]
    for component,row in enumerate(matrix):
        solved=max(range(3),key=lambda i:abs(row[i]))
        others=[i for i in range(3) if i!=solved]
        for _ in range(1000):
            linear=[0.,0.,0.]
            scale=10**rng.uniform(-2,3)
            for i in others:
                linear[i]=scale*rng.uniform(-1,1)
            target=scale*rng.choice((-1,0,1))*2**-24
            linear[solved]=(target-math.fsum(row[i]*linear[i] for i in others))/row[solved]
            encoded=tuple(map(o.f32,map(o.encode,linear)))
            lab=o.encoded_lab(encoded)
            # Keep this arithmetic diagnostic away from the separate mandated
            # identity guard. L-guard behavior has its own exact direct tests.
            if lab[0]>.01:
                fixtures.append((component,encoded))
    outputs=d.native([('P',rgb,PARAMS) for _,rgb in fixtures],d.EXE)
    worst={'normalized_error':0.}
    failures=0
    counts=[0,0,0]
    for (component,rgb),actual in zip(fixtures,outputs):
        counts[component]+=1
        expected=o.apply(rgb,*PARAMS)
        error=maximum_delta(actual,expected.rgb)/max(1.,*map(abs,expected.rgb))
        failures+=int(not all(map(math.isfinite,actual)) or error>2**-13)
        if error>worst['normalized_error']:
            worst={'normalized_error':error,'component':component,
                   'input_encoded':rgb,'native_encoded':actual,
                   'oracle_encoded':expected.rgb,'oracle_path':expected.path}
    return {'samples':len(fixtures),'plane_counts':counts,
            'outside_existing_empirical_envelope_or_nonfinite':failures,'worst':worst}


def routing_seams():
    a,c=lms_at(0.),lms_at(1.)
    slope=tuple(y-x for x,y in zip(a,c))
    fixtures=[]
    for sign in (-1.,1.):
        ratio=sign*2**-8
        u=(ratio*a[2]-a[0])/(slope[0]-ratio*slope[2])
        for i in range(-32,33):
            value=u+i*2**-24
            fixtures.append(tuple(map(o.f32,map(o.encode,linear_at(value)))))
    outputs=d.native([('P',rgb,PARAMS) for rgb in fixtures],d.EXE)
    errors=[maximum_delta(actual,o.apply(rgb,*PARAMS).rgb)
            for rgb,actual in zip(fixtures,outputs)]
    return {'samples':len(fixtures),'max_encoded_native_oracle_error':max(errors),
            'outside_existing_empirical_envelope':sum(e>2**-13 for e in errors)}
