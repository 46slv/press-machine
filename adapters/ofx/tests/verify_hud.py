"""Compile and run portable Graph models; does not compile/load the OFX overlay."""
from pathlib import Path
import os
import hashlib
import json
import platform
from datetime import datetime, timezone
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
build = root / 'build/graph'
results = root / 'results/v3_curve/graph'
build.mkdir(parents=True, exist_ok=True)
results.mkdir(parents=True, exist_ok=True)
subprocess.run([sys.executable, str(root / 'tests/verify_hud_source.py')], check=True)
for source, receipt in [('HudPlacementTests', 'HUD_PLACEMENT'), ('HudTests', 'HUD_MODEL'), ('DensityGraphTests', 'DENSITY_GRAPH')]:
    target = build / (source + ('.exe' if os.name == 'nt' else ''))
    if os.name == 'nt':
        command = ['cl', '/nologo', '/O2', '/EHsc', '/std:c++17', '/fp:strict',
                   str(root / 'tests' / (source + '.cpp')), '/Fe:' + str(target)]
    else:
        command = ['g++', '-O2', '-std=c++17', '-ffp-contract=off',
                   str(root / 'tests' / (source + '.cpp')), '-o', str(target)]
    subprocess.run(command, check=True, cwd=build)
    subprocess.run([str(target), str(results / (receipt + '.json'))], check=True, cwd=build)

inputs = ['src/HudOverlay.hpp', 'src/HudPlacement.hpp', 'tests/HudPlacementTests.cpp', 'src/HudModel.hpp', 'src/DensityGraph.hpp',
          'src/Plugin.cpp', 'generate_descriptors.py', 'generated/Descriptors.hpp',
          'generated/PixelCore.hpp', 'generated/ParameterValues.hpp',
          'tests/HudTests.cpp', 'tests/DensityGraphTests.cpp',
          'tests/verify_hud.py', 'tests/verify_hud_source.py']
manifest = {
    'status': 'SOURCE_CHECKS_PASS_NOT_HOST_VALIDATED',
    'tested_at_UTC': datetime.now(timezone.utc).isoformat(),
    'platform': platform.platform(),
    'compiler': 'MSVC /fp:strict /O2' if os.name == 'nt' else subprocess.check_output(['g++', '--version'], text=True).splitlines()[0],
    'source_sha256_canonical_LF': {name: hashlib.sha256((root / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() for name in inputs},
    'native_OFX_overlay_compiled': False,
    'Host_graph_export_acceptance': False,
}
(results / 'GRAPH_SOURCE_CHECKPOINT.json').write_text(json.dumps(manifest, indent=2) + '\n')
