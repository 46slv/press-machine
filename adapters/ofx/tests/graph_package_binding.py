"""Accidental stale-build/substitution detection; not signed provenance or Host proof."""
from pathlib import Path
import argparse
import hashlib
import json
from verify_graph_gate import verify as verify_graph

VERSION = 1
BINARY = 'Contents/Win64/PressMachineV3CurveDev.ofx'
RECORD = 'Contents/Resources/GRAPH_BUILD_BINDING.json'
INPUTS = (
    'CMakeLists.txt', 'build.ps1', 'SelectBuildGenerator.ps1', 'cmake/MandatoryGraphGate.cmake',
    'src/Plugin.cpp', 'src/HudOverlay.hpp', 'src/HudModel.hpp', 'src/HudPlacement.hpp',
    'src/DensityGraph.hpp', 'src/NeutralHueGraph.hpp', 'generated/Descriptors.hpp',
    'generated/ParameterValues.hpp', 'generated/PixelCore.hpp', 'generate_descriptors.py',
    '../../parameters/press_machine_v3_curve.json',
    'tests/verify_graph_gate.py', 'tests/graph_package_binding.py', 'tests/verify_package_v3.py',
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources(root):
    return {name: sha((root / name).read_bytes().replace(b'\r\n', b'\n')) for name in INPUTS}


def expected(root, bundle):
    verify_graph(root)
    binary = bundle / BINARY
    if binary.is_symlink() or binary.resolve().parent != (bundle / 'Contents/Win64').resolve():
        raise ValueError('Binding binary must be the fixed bundle file, not a redirected symlink')
    return {'format_version': VERSION, 'binary_relative_path': BINARY,
            'binary_sha256': sha(binary.read_bytes()), 'source_sha256_canonical_lf': sources(root)}


def write(root, bundle, target):
    root, bundle, target = Path(root), Path(bundle), Path(target)
    if target.absolute() != (bundle / BINARY).absolute():
        raise ValueError('POST_BUILD target is not the fixed product binary path')
    data = expected(root, bundle)
    path = bundle / RECORD
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('Binding sidecar must not be a symlink')
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)
    return data


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate binding key: ' + key)
        result[key] = value
    return result


def verify(root, bundle):
    root, bundle = Path(root), Path(bundle)
    path = bundle / RECORD
    if path.is_symlink():
        raise ValueError('Binding sidecar must not be a symlink')
    data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=no_duplicates)
    if not isinstance(data, dict) or type(data.get('format_version')) is not int or data['format_version'] != VERSION:
        raise ValueError('Unsupported or malformed Graph binding version')
    wanted = expected(root, bundle)
    if data != wanted:
        raise ValueError('Graph binding mismatch: fixed binary path, binary hash or current source hashes differ')
    return {'status': 'PASS_CURRENT_SOURCE_BINARY_BINDING', 'format_version': VERSION,
            'binary_sha256': data['binary_sha256'], 'source_files': len(INPUTS),
            'signed_provenance': False, 'graph_runtime_verified': False, 'host_acceptance': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--target', type=Path, help='Write mode: actual CMake target binary')
    a = p.parse_args()
    try:
        result = write(a.root, a.bundle, a.target) if a.target else verify(a.root, a.bundle)
        print(json.dumps(result))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, 'Graph package binding failed: ' + str(exc) + '\n')
