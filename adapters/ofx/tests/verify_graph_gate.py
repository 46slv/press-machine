"""Mandatory current-source Graph structure gate, not binary/Host qualification."""
from pathlib import Path
import argparse
import json
import re


def code(path):
    # Strip comments while preserving string literals (labels may contain //).
    text = path.read_text(encoding='utf-8')
    return re.sub(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|//[^\n]*|/\*.*?\*/',
                  lambda m: m.group(1) or '', text, flags=re.S)


def verify(root):
    root = Path(root)
    plugin = code(root / 'src/Plugin.cpp')
    overlay = code(root / 'src/HudOverlay.hpp')
    descriptors = code(root / 'generated/Descriptors.hpp')
    cmake = re.sub(r'#[^\n]*', '', (root / 'CMakeLists.txt').read_text())
    checks = {
        'cmake_gate_dependency': 'include(cmake/MandatoryGraphGate.cmake)' in cmake and 'pressmachine_require_graph(PressMachine "${CMAKE_CURRENT_SOURCE_DIR}")' in cmake,
        'overlay_include': '#include "HudOverlay.hpp"' in plugin,
        'effect_registration': bool(re.search(r'void PressMachineFactory::describe\([^\n]*\)\s*\{[^}]*pmhud::describe\(d\);', plugin)),
        'parameter_registration': 'defineParameters(d);' in plugin,
        'graph_descriptor': 'd.defineBooleanParam("pm_graph")' in descriptors and 'page->addChild(*graph)' in descriptors,
        'graph_viewer_only': all(x in descriptors for x in ['graph->setDefault(false)', 'graph->setAnimates(false)', 'graph->setEvaluateOnChange(false)']),
        'overlay_descriptor': 'OFX::DefaultEffectOverlayDescriptor<Descriptor,Overlay>' in overlay,
        'overlay_entry': 'propSetPointer(kOfxImageEffectPluginPropOverlayInteractV1,(void*)descriptor.getMainEntry())' in overlay,
        'graph_handle': 'fetchBooleanParam("pm_graph")' in overlay,
        'redraw_graph': 'addParamToSlaveTo(graph)' in overlay,
        'redraw_controls': 'handles.forEach([this](auto*param){addParamToSlaveTo(param);});' in overlay,
        'draw_override': 'bool draw(const OFX::DrawArgs&a) override' in overlay,
        'draw_toggle': 'if(!graph->getValueAtTime(a.time))return false;' in overlay,
        'draw_panels': 'drawPanels(cache.get(),' in overlay,
        'opengl_linkage': bool(re.search(r'target_link_libraries\(PressMachine\s+PRIVATE\s+[^)]*\bopengl32\b', cmake)),
    }
    schema = json.loads((root.parents[1] / 'parameters/press_machine_v3_curve.json').read_text())
    checks['redraw_schema_complete'] = re.findall(r'visitor\((\w+)\);', descriptors) == [p['id'] for p in schema]
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise ValueError('Mandatory Graph gate failed: ' + ', '.join(failed))
    return {'status': 'PASS_SOURCE_STRUCTURE_NOT_HOST', 'checks': len(checks),
            'binary_provenance_verified': False, 'host_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root)))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')
