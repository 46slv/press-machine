"""Compiled portable POST_BUILD fixture; not a real Windows OFX/Host test."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
from graph_package_binding import INPUTS, BINARY, RECORD, verify

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='pm-graph-binding-') as td:
    base = Path(td)
    source = base / 'source/adapters/ofx'
    for name in INPUTS:
        dest = source / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, dest)
    schema = source.parents[1] / 'parameters/press_machine_v3_curve.json'
    schema.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root.parents[1] / 'parameters/press_machine_v3_curve.json', schema)
    fixture = base / 'fixture'
    fixture.mkdir()
    (fixture / 'fixture.cpp').write_text('int main(){return 0;}\n')
    (fixture / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(GraphBindingFixture LANGUAGES CXX)
add_executable(PressMachine fixture.cpp)
set_target_properties(PressMachine PROPERTIES OUTPUT_NAME "PressMachineV3CurveDev" SUFFIX ".ofx"
 RUNTIME_OUTPUT_DIRECTORY "${BUNDLE}/Contents/Win64" RUNTIME_OUTPUT_DIRECTORY_RELEASE "${BUNDLE}/Contents/Win64")
include("${PM_ROOT}/cmake/MandatoryGraphGate.cmake")
pressmachine_require_graph(PressMachine "${PM_ROOT}")
pressmachine_bind_graph_package(PressMachine "${PM_ROOT}" "${BUNDLE}")
''')
    build = base / 'build'
    bundle = base / 'PressMachineV3CurveDev.ofx.bundle'
    subprocess.run(['cmake', '-S', str(fixture), '-B', str(build), '-DPM_ROOT=' + source.as_posix(),
                    '-DBUNDLE=' + bundle.as_posix(), '-DPython3_EXECUTABLE=' + sys.executable], check=True)
    subprocess.run(['cmake', '--build', str(build), '--config', 'Release', '--target', 'PressMachine'], check=True)
    verify(source, bundle)
    record = bundle / RECORD
    original = record.read_bytes()
    binary = bundle / BINARY
    binary_original = binary.read_bytes()
    failures = []
    def rejects(label):
        try:
            verify(source, bundle)
        except (OSError, ValueError, KeyError, TypeError):
            failures.append(label)
        else:
            raise RuntimeError('Mutation escaped: ' + label)
    record.unlink(); rejects('missing'); record.write_bytes(original)
    binary.write_bytes(binary_original + b'changed'); rejects('different_binary'); binary.write_bytes(binary_original)
    path = source / 'src/HudOverlay.hpp'
    old = path.read_bytes(); path.write_bytes(old + b'\n// changed source\n'); rejects('stale_source'); path.write_bytes(old)
    for label, key, value in [('path', 'binary_relative_path', '../other.ofx'), ('version', 'format_version', 2),
                              ('boolean_version', 'format_version', True), ('hash', 'binary_sha256', '0'*64),
                              ('missing_source', 'source_sha256_canonical_lf', {})]:
        data = json.loads(original); data[key] = value
        record.write_text(json.dumps(data)); rejects(label)
    for label, data in [('malformed', '{'), ('wrong_type', '[]'), ('duplicate_key', '{"format_version":1,"format_version":1}')]:
        record.write_text(data); rejects(label)
    record.write_bytes(original)
    # Canonical LF permits equivalent checkout line endings, not source differences.
    for name in INPUTS:
        p = source / name
        p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
    verify(source, bundle)
    # Integration: normal package entry rejects mismatched binary before DLL load.
    binary.write_bytes(binary_original + b'changed')
    result = subprocess.run([sys.executable, str(source / 'tests/verify_package_v3.py'), str(bundle)], capture_output=True, text=True)
    if result.returncode == 0 or 'Graph binding mismatch' not in result.stderr:
        raise RuntimeError('Package entry did not fail before DLL loading: ' + result.stderr)
    failures.append('package_entry_before_load')
print(json.dumps({'status':'PASS', 'compiled_post_build_binding':True, 'negative_cases':failures,
                  'canonical_lf_pass':True, 'windows_ofx_binary':False, 'host_acceptance':False}))
