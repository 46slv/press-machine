"""Negative source mutations and portable execution of the product's CMake gate module.
The fixture uses a marker target, not the Windows OFX SDK/compiler or a real bundle.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
from verify_graph_gate import verify

root = Path(__file__).resolve().parents[1]
repo = root.parents[1]
verify(root)
mutations = [
    ('CMakeLists.txt', 'pressmachine_require_graph(PressMachine "${CMAKE_CURRENT_SOURCE_DIR}")', '', 'cmake_gate_dependency'),
    ('src/Plugin.cpp', 'pmhud::describe(d);', '// pmhud::describe(d);', 'effect_registration'),
    ('src/Plugin.cpp', 'defineParameters(d);', '', 'parameter_registration'),
    ('generated/Descriptors.hpp', 'd.defineBooleanParam("pm_graph")', 'd.defineBooleanParam("missing_graph")', 'graph_descriptor'),
    ('generated/Descriptors.hpp', 'graph->setEvaluateOnChange(false)', 'graph->setEvaluateOnChange(true)', 'graph_viewer_only'),
    ('generated/Descriptors.hpp', 'visitor(pm_pre);', '', 'redraw_schema_complete'),
    ('src/HudOverlay.hpp', 'kOfxImageEffectPluginPropOverlayInteractV1', 'missingOverlay', 'overlay_entry'),
    ('src/HudOverlay.hpp', 'addParamToSlaveTo(graph);', '', 'redraw_graph'),
    ('src/HudOverlay.hpp', 'handles.forEach([this](auto*param){addParamToSlaveTo(param);});', '', 'redraw_controls'),
    ('src/HudOverlay.hpp', 'drawPanels(cache.get(),', 'missingPanels(cache.get(),', 'draw_panels'),
    ('CMakeLists.txt', 'shell32 ole32 opengl32', 'shell32 ole32', 'opengl_linkage'),
]
with tempfile.TemporaryDirectory(prefix='pm-graph-gate-') as td:
    base = Path(td)
    fake = base / 'source/adapters/ofx'
    paths = ['src/Plugin.cpp', 'src/HudOverlay.hpp', 'generated/Descriptors.hpp',
             'CMakeLists.txt', 'tests/verify_graph_gate.py', 'tests/verify_package_v3.py', 'tests/graph_package_binding.py', 'cmake/MandatoryGraphGate.cmake']
    for name in paths:
        dest = fake / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, dest)
    schema = base / 'source/parameters/press_machine_v3_curve.json'
    schema.parent.mkdir(parents=True)
    shutil.copyfile(repo / 'parameters/press_machine_v3_curve.json', schema)
    for name, old, new, expected in mutations:
        path = fake / name
        original = path.read_text()
        if old not in original:
            raise RuntimeError('Mutation no longer matches: ' + expected)
        path.write_text(original.replace(old, new))
        try:
            verify(fake)
        except ValueError as exc:
            if expected not in str(exc):
                raise
        else:
            raise RuntimeError('Mutation escaped: ' + expected)
        finally:
            path.write_text(original)
    # The same module and dependency used by the real product, with no SDK required.
    fixture = base / 'fixture'
    fixture.mkdir()
    (fixture / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(GraphGateFixture NONE)
add_custom_target(PressMachine COMMAND "${CMAKE_COMMAND}" -E touch "${CMAKE_BINARY_DIR}/product-ran")
include("${PM_ROOT}/cmake/MandatoryGraphGate.cmake")
pressmachine_require_graph(PressMachine "${PM_ROOT}")
''')
    build = base / 'build'
    subprocess.run(['cmake', '-S', str(fixture), '-B', str(build), '-DPM_ROOT=' + fake.as_posix(),
                    '-DPython3_EXECUTABLE=' + sys.executable], check=True)
    command = ['cmake', '--build', str(build), '--target', 'PressMachine']
    subprocess.run(command, check=True)
    marker = build / 'product-ran'
    if not marker.exists():
        raise RuntimeError('Valid CMake product target did not run')
    marker.unlink()
    plugin = fake / 'src/Plugin.cpp'
    plugin.write_text(plugin.read_text().replace('pmhud::describe(d);', '// removed registration'))
    rejected = subprocess.run(command, capture_output=True, text=True)
    if rejected.returncode == 0 or marker.exists() or 'effect_registration' not in rejected.stdout + rejected.stderr:
        raise RuntimeError('Broken CMake build was not blocked before product target: ' + rejected.stdout + rejected.stderr)
    rejected = subprocess.run([sys.executable, str(fake / 'tests/verify_package_v3.py')], capture_output=True, text=True)
    if rejected.returncode == 0 or 'effect_registration' not in rejected.stdout + rejected.stderr:
        raise RuntimeError('Package verifier did not reject broken source before binary loading')
    # Removing generated descriptors also must fail closed.
    (fake / 'generated/Descriptors.hpp').unlink()
    rejected = subprocess.run([sys.executable, str(fake / 'tests/verify_graph_gate.py'), '--root', str(fake)], capture_output=True, text=True)
    if rejected.returncode == 0:
        raise RuntimeError('Missing generated descriptors escaped')
print(json.dumps({'status': 'PASS', 'negative_mutations': len(mutations),
                  'cmake_valid_product_ran': True, 'cmake_missing_registration_blocked_product': True,
                  'missing_generated_descriptor_rejected': True, 'package_broken_source_rejected': True, 'windows_ofx_build': False,
                  'host_acceptance': False}))
