"""Source isolation for the30-value Makeup extension of existing v3 HUD, not Host acceptance."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

r = Path(__file__).resolve().parents[3]
o = r / 'adapters/ofx'
base = 'c0f475565f5d4cd82e8e23f6dee575b6fe930a49'
legacy = '33c72a8b8d25a5bad8355aa2f27594cec5939c8e'

def baseline(path):
    return subprocess.check_output(['git', 'show', base + ':' + path], cwd=r)

frozen = [
    'parameters/press_machine_v2.json', 'parameters/press_machine_v3.json',
    'parameters/press_machine_v3_curve.json', 'adapters/ofx/src/CudaRunner.cpp',
    'adapters/ofx/src/Kernel.cu', 'adapters/ofx/tests/NativeV3.cpp',
    'adapters/ofx/generated/ParameterValues.hpp',
    'adapters/ofx/generated/PressMachine_V3_Curve_TEST.dctl',
    'adapters/ofx/SOURCE_MANIFEST_V3_CURVE.json',
    'adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl',
]
approved_makeup_changes={'parameters/press_machine_v3_curve.json','adapters/ofx/generated/ParameterValues.hpp','adapters/ofx/generated/PressMachine_V3_Curve_TEST.dctl','adapters/ofx/SOURCE_MANIFEST_V3_CURVE.json','adapters/ofx/tests/NativeV3.cpp','core/press_machine/VNextHue.dctlh','core/press_machine/PixelPipeline.dctlh','core/press_machine/AlphaAndIdentity.hpp.in'}
frozen += sorted(p.relative_to(r).as_posix() for p in (r / 'core/press_machine').glob('*') if p.is_file())
frozen=[p for p in frozen if p not in approved_makeup_changes]
hashes = {}
for path in frozen:
    # Canonical LF content: Windows may check out .hpp.in templates as CRLF.
    old = baseline(path).replace(b'\r\n', b'\n')
    new = (r / path).read_bytes().replace(b'\r\n', b'\n')
    assert old == new, 'Frozen source changed: ' + path
    hashes[path] = hashlib.sha256(new).hexdigest()

old = baseline('adapters/ofx/src/Plugin.cpp').decode()
new = (o / 'src/Plugin.cpp').read_text()
assert new.replace('#include "HudOverlay.hpp"\n', '').replace(' pmhud::describe(d);\n', '') == old
assert 'pm_graph' not in new, 'Graph leaked into processor/effect class'
schema = json.loads((r / 'parameters/press_machine_v3_curve.json').read_text())
ids = [p['id'] for p in schema]
assert len(ids) == len(set(ids)) == 30
assert 'pm_graph' not in ids and 'pm_hue_points_index' not in ids

generated = (o / 'generated/Descriptors.hpp').read_text()
assert 'graph->setDefault(false)' in generated and 'graph->setAnimates(false)' in generated
assert 'graph->setEvaluateOnChange(false)' in generated
assert re.findall(r'visitor\((\w+)\);', generated) == ids, 'Redraw slaves must cover schema order exactly'
assert len(re.findall(r'v\[\d+\]=', generated)) == len(ids), 'Descriptor reader ABI'
for index, param in enumerate(schema):
    name = param['id']
    if param['kind'] == 'choice':
        assert f'{name}->getValueAtTime(time,choice);v[{index}]=choice;' in generated
    else:
        assert f'v[{index}]={name}->getValueAtTime(time);' in generated
for name in ['PixelCore.hpp', 'ParameterValues.hpp', 'DctlReferenceV3Curve.hpp']:
    assert 'pm_graph' not in (o / 'generated' / name).read_text(), name
manifest = json.loads((o / 'SOURCE_MANIFEST_V3_CURVE.json').read_text())
assert hashlib.sha256((o / 'generated/PixelCore.hpp').read_bytes()).hexdigest() == manifest['shared_core_sha256']
assert hashlib.sha256((o / 'generated/PressMachine_V3_Curve_TEST.dctl').read_bytes()).hexdigest() == manifest['generated_dctl_sha256']

overlay = (o / 'src/HudOverlay.hpp').read_text()
model = (o / 'src/HudModel.hpp').read_text()
density = (o / 'src/DensityGraph.hpp').read_text()
neutral = (o / "src/NeutralHueGraph.hpp").read_text()
assert "pm::pmvn_hue_curve(" in neutral
assert "pm::pmvpy_Y(input)" in neutral
assert "makeNeutralHueGraph(p)" in model
for source in [overlay, model, density, neutral]:
    for forbidden in ['setValue(', 'setValueAtTime(', 'fetchImage(', 'pm::pixel(', 'glClear(', 'swapBuffers(']:
        assert forbidden not in source, forbidden
    assert 'pm_hue_points_index' not in source
assert 'kOfxImageEffectPluginPropOverlayInteractV1' in overlay
assert 'handles.forEach([this](auto*param){addParamToSlaveTo(param);});' in overlay
assert 'std::array<double,kParameterCount> values' in overlay
assert 'std::array<double,kParameterCount> previous' in model
assert 'std::array<double,25>' not in overlay + model
assert 'if(!graph->getValueAtTime(a.time))return false;' in overlay
assert 'pm::pmvn_anchor(p.pm_hue_pattern,anchor)' in model
assert 'pm::pmvn_pattern_count(p.pm_hue_pattern)' in model
assert 'pm::pmvn_curve_q_ref(' in model and 'pm::pmvn_drive(' in model
assert 'z.conditioned' not in density and 'z.comp' not in density and 'z.density' not in density
assert 'pm::pmvpy_Y(z.hue)' in density and 'pm::pmvpy_Y(z.look)' in density
assert 'pm::pmvp_lab(z.hue)' in density and 'pm::pmvp_lab(z.look)' in density
assert 'pm::pmvn_process_makeup(' in density
# Preserve legacy rendering infrastructure rather than substitute a new HUD.
# Pinned canonical section hashes avoid requiring the old feature branch in CI.
legacy_sections = [('inline const unsigned char* glyph', 'inline void densityPanel', 'b97df6835e0f096207e07ad98554ec18d49ea870706642cf6f870e1dabf5c975'), ('class Descriptor:', '\n}\n', '68e4c12c9324b015525175ba31518bfa6e14b752593403c22fe84681b976716a')]
for start, end, sha in legacy_sections:
    section = overlay.split(start, 1)[1].split(end, 1)[0]
    assert hashlib.sha256(section.encode()).hexdigest() == sha, start
assert ids[:29] == [p['id'] for p in json.loads(baseline('parameters/press_machine_v3_curve.json'))]
old29=json.loads(__import__('subprocess').check_output(['git','show','f0e3160:parameters/press_machine_v3_curve.json'],cwd=r))
assert [{k:v for k,v in p.items() if k!='group'} for p in schema[:29]]==[{k:v for k,v in p.items() if k!='group'} for p in old29]
assert ids[29]=='pm_makeup' and schema[29]['default']==100 and schema[29]['min']==0 and schema[29]['max']==200
assert 'opengl32' in (o / 'CMakeLists.txt').read_text()

report = {
    'status': 'PASS', 'source_baseline': base, 'reused_hud_baseline': legacy,
    'frozen_file_sha256_canonical_LF': hashes, 'shared_core_sha256': manifest['shared_core_sha256'],
    'processor_and_image_effect_class_byte_identical': True,
    'plugin_identity_and_version_unchanged': True, 'core_parameter_count': len(ids),
    'redraw_slave_parameter_ids': ids, 'graph_ofx_only_default_off': True,
    'graph_nonanimated_no_evaluate_hint': True,
    'legacy_glyphs_GL_state_panels_plots_and_V1_registration_preserved': True,
    'density_endpoints': 'protected Hue -> protected Look using original-input Look protection',
    'host_export_pixel_test': False, 'native_Windows_build': False,
}
results = o / 'results/v3_curve/graph'
results.mkdir(parents=True, exist_ok=True)
(results / 'HUD_SOURCE_SEPARATION.json').write_text(json.dumps(report, indent=2) + '\n')
print('HUD source separation PASS:', len(hashes), 'frozen files; processing classes and plugin ID unchanged; approved core delta;30 redraw slaves')
