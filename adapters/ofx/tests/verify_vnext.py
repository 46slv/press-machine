"""Focused v3 source qualification. Does not claim Resolve/CUDA/visual acceptance."""
from pathlib import Path
import ctypes as C
import hashlib
import json
import math
import os
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SCHEMA = json.loads((REPO / 'parameters/press_machine_v3.json').read_text())
BUILD = ROOT / 'build'
BUILD.mkdir(exist_ok=True)
RESULTS = ROOT / 'results/v3'
RESULTS.mkdir(parents=True, exist_ok=True)
LIB = BUILD / ('VNextNative.dll' if os.name == 'nt' else 'libvnext_native.so')
if os.name == 'nt':
    command = ['cl', '/nologo', '/O2', '/EHsc', '/std:c++17', '/fp:strict', '/LD', str(ROOT / 'tests/NativeV3.cpp'), '/link', '/OUT:' + str(LIB)]
else:
    command = ['g++', '-O2', '-std=c++17', '-shared', '-fPIC', '-ffp-contract=off', str(ROOT / 'tests/NativeV3.cpp'), '-o', str(LIB)]
subprocess.run(command, check=True, cwd=BUILD)
lib = C.CDLL(str(LIB))
D = C.POINTER(C.c_double)
F = C.POINTER(C.c_float)
lib.pm_vnext_scalar.argtypes = [C.c_double] * 4 + [D]
lib.pm_vnext_target.argtypes = [C.c_double] * 4 + [C.c_int, D]
lib.pm_vnext_hue.argtypes = [D, C.c_double, C.c_double, C.c_int, C.c_double, C.c_double, C.c_double, D]
lib.pm_vnext_stages.argtypes = [D, D, D]
lib.pm_vnext_legacy_neutral_hue.argtypes = [D, D, D]
lib.pm_vnext_density.argtypes = [D, D, D]
lib.pm_vnext_y.argtypes = [D]
lib.pm_vnext_y.restype = C.c_double
lib.pm_eval.argtypes = [F, D, C.c_int, F]
lib.pm_dctl_eval.argtypes = [F, D, F]
lib.pm_identity.argtypes = [D]

counts = {}
metrics = {}
def check(condition, group, detail=''):
    counts[group] = counts.get(group, 0) + 1
    assert condition, f'{group}: {detail}'
def arr(x): return (C.c_double * len(x))(*x)
def params(**updates):
    values = {p['id']: p['default'] for p in SCHEMA}
    values.update(updates)
    return arr([values[p['id']] for p in SCHEMA])
def stage(x, p):
    out = (C.c_double * 17)()
    lib.pm_vnext_stages(arr(x), p, out)
    return [list(out[i:i+3]) for i in range(0, 15, 3)], list(out[15:])
def target(a, b, y, angle, pattern):
    out = (C.c_double * 3)()
    lib.pm_vnext_target(a, b, y, angle, pattern, out)
    return out[1], out[2]
def error(x, y): return max(abs(a-b) for a, b in zip(x, y))
def tolerance(x, scale=2e-11): return scale * max(1.0, *(abs(a) for a in x))

# Independently evaluated binary64 geometry from the specification, not core helpers.
PHASE = 0.72821991608931957
OFFSETS = [[0], [0, 30, 330], [0, 180], [0, 150, 210], [0, 120, 240], [0, 90, 180, 270]]
KR, KG, KB = 26158966/99577255, 472592308/697040785, 8267143/139408157
def reference_target(a, b, y, angle, pattern):
    phi = PHASE + math.radians(angle)
    if pattern == 0:
        ux, uy = math.cos(phi), math.sin(phi)
        dr, db = 2*(1-KR)*ux, -2*(1-KB)*uy
        dg = -(KR*dr + KB*db)/KG
        rho = max(y, 0)/-min(dr, dg, db)
        along = max(rho, a*ux+b*uy)
        return along*ux, along*uy
    anchors = [math.radians(x) for x in OFFSETS[pattern]]
    h = math.atan2(b, a)-phi
    ds = [(h-x+math.pi) % math.tau-math.pi for x in anchors]
    i = min(range(len(ds)), key=lambda j: abs(ds[j]))
    d = ds[i]
    gap = ((anchors[(i+1) % len(anchors)]-anchors[i]) % math.tau if d > 0 else
           (anchors[i]-anchors[(i-1) % len(anchors)]) % math.tau)
    H = gap/2
    u = min(1, abs(d)/H)
    f = (.1*u+.9*(u**3-.5*u**4))/.55
    q = u*u*(3-2*u)
    h_target = phi+anchors[i]+math.copysign(H*f, d)
    r = math.hypot(a, b)*(1-q)
    return r*math.cos(h_target), r*math.sin(h_target)

max_scalar = max_geometry = max_y = 0.0
previous = -1.0
for i in range(1001):
    u = i/1000
    y = 0 if i == 0 else .18*2**(-20+40*u)
    out = (C.c_double * 3)()
    bias, split = (100 if i % 2 else -100), (-300 if i % 3 else 300)
    lib.pm_vnext_scalar(y, bias, split, u, out)
    q = (math.sqrt(max(y, 0))-math.sqrt(.18))/(math.sqrt(max(y, 0))+math.sqrt(.18))
    w = math.tanh(math.log(2)*(bias/100+split/100*q))
    f = (.1*u+.9*(u**3-.5*u**4))/.55
    max_scalar = max(max_scalar, error(out, [q, w, f]))
    check(error(out, [q, w, f]) < 2e-12, 'scalar_reference', str(list(out)))
    check(out[2] > previous, 'pattern_curve_monotonic')
    check(abs(out[1]) < 1, 'drive_bounded')
    previous = out[2]
for y, expected in [(0, -1), (.18, 0), (.72, 1/3), (2.88, .6), (-5, -1)]:
    out = (C.c_double * 3)();lib.pm_vnext_scalar(y, 0, 0, 0, out)
    check(abs(out[0]-expected) < 2e-14, 'q_reference_values')

for pattern in range(6):
    for phase in [0, 17.3, 360]:
        # API Angle is binary32, so compare the oracle at the same control value.
        phase = C.c_float(phase).value
        for i in range(1024):
            h = math.tau*i/1024
            a, b = math.cos(h), math.sin(h)
            actual = target(a, b, .18, phase, pattern)
            expected = reference_target(a, b, .18, phase, pattern)
            e = error(actual, expected);max_geometry = max(max_geometry, e)
            check(e < 2e-10, 'pattern_reference', f'{pattern} {phase} {i} {e}')
    for offset in OFFSETS[pattern]:
        h = PHASE+math.radians(offset)
        a, b = 2*math.cos(h), 2*math.sin(h)
        check(error(target(a, b, .18, 0, pattern), [a, b]) < 2e-10, 'fixed_anchors')
    for scale in [1e-25, 1e-8, 1, 1e8, 1e25]:
        expected = target(.31, -.57, .18, 0, pattern)
        actual = target(.31*scale, -.57*scale, .18*scale, 0, pattern)
        check(error([x/scale for x in actual], expected) < 2e-10, 'scale_covariance')

for pattern in range(1, 6):
    anchors = [math.radians(x) for x in OFFSETS[pattern]]
    for i, a in enumerate(anchors):
        gap = (anchors[(i+1) % len(anchors)]-a) % math.tau
        h = PHASE+a+gap/2
        left = target(math.cos(h-1e-7), math.sin(h-1e-7), .18, 0, pattern)
        right = target(math.cos(h+1e-7), math.sin(h+1e-7), .18, 0, pattern)
        check(error(left, right) < 2e-10, 'cell_boundary_continuity')
        check(max(abs(x) for x in target(math.cos(h), math.sin(h), .18, 0, pattern)) < 2e-12, 'midpoint_neutral')
    for strength in [0, .25, .5, .75, 1]:
        previous = None
        for j in range(2048):
            h = math.tau*j/2048
            a, b = math.cos(h), math.sin(h)
            ta, tb = target(a, b, .18, 0, pattern)
            a, b = a+strength*(ta-a), b+strength*(tb-b)
            if math.hypot(a, b) < 1e-10:
                continue
            angle = math.atan2(b, a)
            if previous is not None:
                step = (angle-previous+math.pi) % math.tau-math.pi
                check(step >= -1e-10, 'pattern_angular_order', f'{pattern} {strength} {j} {step}')
            previous = angle
    check(error(target(.31, -.57, .18, 0, pattern), target(.31, -.57, .18, 360, pattern)) == 0, 'angle_seam_exact')

rng = random.Random(1203)
samples = [[.18]*3, [0]*3, [-1, .2, 2], [1, 0, 0], [0, 0, 1], [.7, .45, .3], [20, 12, -2]]
samples += [[1e-25, -2e-25, 4e-25], [1e25, -2e25, 4e25], [1e37, -2e37, 3e37]]
samples += [[rng.uniform(-2, 4) for _ in range(3)] for _ in range(50)]
for x in samples:
    y = lib.pm_vnext_y(arr(x))
    for pattern in range(6):
        out = (C.c_double * 3)()
        lib.pm_vnext_hue(arr(x), y, 33, pattern, 70, 80, -300, out)
        check(all(math.isfinite(a) for a in out), 'hue_finite')
        ey = abs(lib.pm_vnext_y(out)-y)/max(1, abs(y), *(abs(a) for a in x))
        max_y = max(max_y, ey)
        check(ey < 3e-8, 'hue_preserves_y', str(ey))
    p = params(pm_pre=130, pm_compression=60, pm_threshold=65, pm_density=180, pm_chroma=-40)
    z, _ = stage(x, p)
    old = (C.c_double*3)();lib.pm_vnext_legacy_neutral_hue(arr(x), p, old)
    check(error(z[4], old) < tolerance(x, 1e-10), 'neutral_hue_legacy_core', f'{x} new={z[4]} old={list(old)}')

for pattern in range(6):
    x = [.7, .45, .3];y = lib.pm_vnext_y(arr(x))
    full = (C.c_double*3)();lib.pm_vnext_hue(arr(x), y, 17, pattern, 100, 0, 0, full)
    for strength in [0, 25, 50, 75, 100]:
        out = (C.c_double*3)();lib.pm_vnext_hue(arr(x), y, 17, pattern, strength, 0, 0, out)
        expected = [a+strength/100*(b-a) for a,b in zip(x, full)]
        check(error(out, expected) < 2e-12, 'direct_strength_displacement')

x = [.7, .45, .3]
base = dict(pm_pre=150, pm_compression=80, pm_threshold=40, pm_hue_compression=70, pm_hue_bias=80, pm_luma_split=150, pm_density=150, pm_chroma=30)
raw, _ = stage(x, params(**base))
for skin in [0, 50, 100]:
    z, keep = stage(x, params(**base, pm_sat_skin=skin))
    expected = [(1-keep[0])*a+keep[0]*b for a, b in zip(x, raw[1])]
    check(error(z[1], expected) < 2e-12, 'comp_net_protection_once')
    z, keep = stage(x, params(**base, pm_density_skin=skin))
    expected = [(1-keep[1])*a+keep[1]*b for a, b in zip(raw[1], raw[3])]
    check(error(z[3], expected) < 2e-12, 'look_net_protection_once')
    check(keep[1] < 1 if skin else keep[1] == 1, 'skin_fixture_eligible')
z, _ = stage(x, params(**base, pm_db=1))
check(error(z[2], z[3]) == 0, 'density_bypass_keeps_hue')
check(error(z[1], z[2]) > 1e-4, 'density_bypass_hue_active')
direct = (C.c_double*3)();lib.pm_vnext_density(arr(raw[2]), params(**base), direct)
check(error(raw[3], direct) < 2e-12, 'post_hue_density_tap')
y_ref = lib.pm_vnext_y(arr(x));lib.pm_vnext_hue(arr(raw[1]), y_ref, 0, 2, 70, 80, 150, direct)
check(error(raw[2], direct) < 2e-12, 'fixed_input_y_reference')
invalid_hue, _ = stage(x, params(**base, pm_hue_pattern=99))
lib.pm_vnext_density(arr(invalid_hue[1]), params(**base), direct)
check(error(invalid_hue[2], invalid_hue[1]) == 0, 'invalid_hue_local_fallback')
check(error(invalid_hue[3], direct) < 2e-12, 'invalid_hue_density_continues')
invalid_density, _ = stage(x, params(**{**base, 'pm_density': float('nan')}))
check(error(invalid_density[2], raw[2]) < 2e-12, 'invalid_density_keeps_hue')
check(error(invalid_density[3], invalid_density[2]) == 0, 'invalid_density_local_fallback')
invalid_pre, _ = stage(x, params(pm_pre=float('nan'), pm_compression=80, pm_threshold=40))
valid_comp, _ = stage(x, params(pm_compression=80, pm_threshold=40))
check(error(invalid_pre[1], valid_comp[1]) == 0, 'invalid_presat_comp_continues')
invalid_final, _ = stage(x, params(**base, pm_sd_t=float('nan')))
check(error(invalid_final[4], raw[3]) == 0, 'invalid_final_keeps_look')
for pattern in range(6):
    z, _ = stage([.18]*3, params(pm_hue_pattern=pattern, pm_hue_bias=100))
    check(error(z[2], [.18]*3) > .01, 'bias_independent_strength_pattern')
z, _ = stage([.001]*3, params(pm_luma_split=300))
check(max(z[2])-min(z[2]) > .001, 'split_colored_black_off')
desat, _ = stage([.001]*3, params(pm_luma_split=300, pm_sd_t=.5, pm_sd_k=.05))
check(max(desat[4])-min(desat[4]) < 1e-12, 'final_black_policy_on')
check(error(desat[4], desat[3]) > 1e-5, 'final_after_look')

parity_cases = 0
for i in range(180):
    p = params(pmi_it=4, pm_pre=rng.uniform(0, 200), pm_compression=rng.uniform(0, 100), pm_hue_pattern=i%6,
               pm_hue_angle=rng.uniform(0, 360), pm_hue_compression=rng.uniform(0, 100), pm_hue_bias=rng.uniform(-100, 100),
               pm_luma_split=rng.uniform(-300, 300), pm_density=rng.uniform(-300, 300), pm_chroma=rng.uniform(-100, 100),
               pm_sat_skin=rng.choice([0, 50, 100]), pm_density_skin=rng.choice([0, 50, 100]))
    pixel = (C.c_float*4)(*[rng.uniform(-2, 10) for _ in range(3)], rng.random())
    a, b = (C.c_float*4)(), (C.c_float*4)()
    lib.pm_eval(pixel, p, 0, a);lib.pm_dctl_eval(pixel, p, b)
    check(bytes(a) == bytes(b), 'generated_dctl_cpu_bit_parity')
    check(a[3] == pixel[3], 'alpha_unchanged')
    check(all(math.isfinite(v) for v in a), 'adapter_finite')
    parity_cases += 1
# All supported input/output profile selector combinations must stay finite and use the same generated-DCTL wiring.
profile_conversion_cases = 0
for ig in range(4):
    for it in range(5):
        for og in range(5):
            for ot in range(6):
                p = params(pmi_ig=ig, pmi_it=it, pmi_og=og, pmi_ot=ot)
                pixel = (C.c_float*4)(.30, .20, .10, 1.0)
                a, b = (C.c_float*4)(), (C.c_float*4)()
                lib.pm_eval(pixel, p, 0, a); lib.pm_dctl_eval(pixel, p, b)
                check(bytes(a) == bytes(b), 'profile_generated_dctl_bit_parity')
                check(all(math.isfinite(v) for v in a), 'profile_conversion_finite')
                check(a[3] == 1.0, 'profile_alpha_unchanged')
                profile_conversion_cases += 1
check(lib.pm_identity(params()) == 1, 'identity_default')
for key in ['pm_hue_bias', 'pm_luma_split']:
    check(lib.pm_identity(params(**{key: 1})) == 0, 'identity_bias_split_active')

result = dict(status='PASS', checks=sum(counts.values()), groups=counts,
              max_scalar_absolute_error=max_scalar, max_geometry_absolute_error=max_geometry,
              max_hue_y_normalized_error=max_y, generated_dctl_cpu_bit_exact_cases=parity_cases, profile_conversion_cases=profile_conversion_cases,
              shared_core_sha256=hashlib.sha256((ROOT/'generated/PixelCore.hpp').read_bytes()).hexdigest(),
              generated_dctl_sha256=hashlib.sha256((ROOT/'generated/PressMachine_V3_Dev_TEST.dctl').read_bytes()).hexdigest(),
              scope='Focused shared-core binary32-pair CPU and CPU-compiled generated-DCTL checks only. CUDA, native OFX SDK build, Resolve, save/reopen, footage, 4K, and user visual acceptance NOT RUN.')
(RESULTS/'FOCUSED_CPU.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
