"""Generate the v3.dev candidate. Released v2 artifacts/evidence are read-only."""
from pathlib import Path
import hashlib
import json
import re

r = Path(__file__).resolve().parent
root = r.parents[1]
schema_path = root / 'parameters/press_machine_v3.json'
schema = json.loads(schema_path.read_text())
assert len(schema) == 27 and len({p['id'] for p in schema}) == 27
(r / 'generated').mkdir(exist_ok=True)
(r / 'results/v3').mkdir(parents=True, exist_ok=True)

def declarations():
    lines = ['struct Parameters {\n']
    for p in schema:
        lines.append(f" {'float' if p['kind'] == 'double' else 'int'} {p['id']};\n")
    lines.append('};\nPM_DEVICE Parameters defaultParameters(){Parameters p{};')
    for p in schema:
        value = str(float(p['default'])) + 'f' if p['kind'] == 'double' else str(p['default'])
        lines.append(f"p.{p['id']}={value};")
    return ''.join(lines) + 'return p;}\n'

def ui_declarations():
    lines = ['// Press Machine v3.dev: Comp -> Hue -> Density. Host qualification pending.']
    for p in schema:
        start = f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, "
        if p['kind'] == 'double':
            line = start + f"DCTLUI_SLIDER_FLOAT, {p['default']}, {p['min']}, {p['max']}, {p['step']})"
        elif p['kind'] == 'bool':
            line = start + f"DCTLUI_CHECK_BOX, {p['default']})"
        else:
            symbols = ', '.join(f"PMV3_{p['id'].upper()}_{i}" for i in range(len(p['options'])))
            labels = ', '.join(p['options'])
            line = start + f"DCTLUI_COMBO_BOX, {p['default']}, {{ {symbols} }}, {{ {labels} }})"
        lines.append(line)
    lines += [
        'DEFINE_UI_TOOLTIP(Hue Angle, "Shared primary hue for Pattern, Bias and Split. Zero follows the skin-reference axis.")',
        'DEFINE_UI_TOOLTIP(Hue Strength, "Direct Pattern displacement. Bias and Split remain active at zero Strength.")',
        'DEFINE_UI_TOOLTIP(Hue Bias, "Positive attracts toward Angle; negative toward Angle plus 180 degrees.")',
        'DEFINE_UI_TOOLTIP(Luma Split, "Positive attracts highlights toward Angle and shadows toward its opposite. Uses fixed input luminance.")',
        'DEFINE_UI_TOOLTIP(Density Bypass, "Bypasses Density only. Hue and Look Skin Protect remain active.")',
    ]
    return '\n'.join(lines) + '\n'

prefix = (root / 'core/press_machine/PlatformPrefix.hpp.in').read_text() + declarations()
math = (root / 'core/press_machine/PixelMath.dctlh').read_text()
hue = (root / 'core/press_machine/VNextHue.dctlh').read_text()
# Insert Hue helpers before the pipeline tail within PixelMath, if that tail calls them.
marker = '// PM_VNEXT_HUE_INSERT'
if marker in math:
    math = math.replace(marker, hue)
else:
    math += '\n' + hue
pipeline = (root / 'core/press_machine/PixelPipeline.dctlh').read_text()
alpha = (root / 'core/press_machine/AlphaAndIdentity.hpp.in').read_text()
core = prefix + math + pipeline + alpha
(r / 'generated/PixelCore.hpp').write_text(core, newline='\n')
dctl_pipeline = pipeline.replace('transform(const Parameters& p,', 'transform(')
for p in schema:
    dctl_pipeline = re.sub(r'\bp\.' + p['id'] + r'\b', p['id'], dctl_pipeline)
dctl = ui_declarations() + math + dctl_pipeline
assert not re.search(r'\bp\.', dctl_pipeline), 'Unmapped parameter in DCTL pipeline'
(r / 'generated/PressMachine_V3_Dev_TEST.dctl').write_text(dctl, newline='\n')
sha = lambda b: hashlib.sha256(b).hexdigest()
manifest = dict(status='GENERATED_NOT_HOST_VALIDATED', plugin_identifier='com.46slv.PressMachine.v3.dev',
                parameter_count=len(schema), schema_sha256=sha(schema_path.read_bytes()),
                shared_core_sha256=sha(core.encode()), generated_dctl_sha256=sha(dctl.encode()),
                immutable_baseline_sha256=sha((root / 'adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl').read_bytes()),
                scope='v3 development source generation only; no v2 numerical-equivalence or Host acceptance claim')
(r / 'SOURCE_MANIFEST_V3.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
# CPU-compiled DCTL adapter: catches generated UI IDs, defaults and transform wiring.
# This is not a Resolve DCTL compiler or GPU execution receipt.
guards = re.findall(r'^#ifndef\s+(PRESSMACHINE_\w+)', dctl, re.M)
wrapper = '#pragma once\n' + ''.join('#undef ' + g + '\n' for g in guards)
wrapper += '''#define __DEVICE__ inline
#define PMUI_DCTLUI_SLIDER_FLOAT(name,value) static thread_local float name=value;
#define PMUI_DCTLUI_CHECK_BOX(name,value) static thread_local int name=value;
#define PMUI_DCTLUI_COMBO_BOX(name,value) static thread_local int name=value;
#define DEFINE_UI_PARAMS(name,label,kind,value,...) PMUI_##kind(name,value)
#define DEFINE_UI_TOOLTIP(...)
namespace generated_dctl {
struct float2{float x,y;}; struct float3{float x,y,z;};
inline float2 make_float2(float x,float y){return {x,y};}
inline float3 make_float3(float x,float y,float z){return {x,y,z};}
#include "PressMachine_V3_Dev_TEST.dctl"
inline void readValues(const double* v){
'''
for i, p in enumerate(schema):
    wrapper += f"{p['id']}=({'float' if p['kind']=='double' else 'int'})v[{i}];\n"
wrapper += '''}
}
#undef __DEVICE__
#undef DEFINE_UI_PARAMS
#undef DEFINE_UI_TOOLTIP
#undef PMUI_DCTLUI_SLIDER_FLOAT
#undef PMUI_DCTLUI_CHECK_BOX
#undef PMUI_DCTLUI_COMBO_BOX
'''
(r / 'generated/DctlReferenceV3.hpp').write_text(wrapper, newline='\n')
