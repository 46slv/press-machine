"""Compile and mock-test this folder only. Never connect to Resolve."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
from pathlib import Path
import platform
import unittest

import pressmachine_fusion as pm
import test_pressmachine_fusion


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="OFFLINE_VALIDATION.json", help="New JSON filename; never overwrite")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    paths = ["pressmachine_fusion.py", "test_pressmachine_fusion.py", "validate_offline.py",
             "schema/press_machine_v2.json", "README_JA.md", "HOST_VERIFICATION.json"]
    compile_results = {}
    for name in paths:
        if name.endswith(".py"):
            compile((root / name).read_text(encoding="utf-8"), name, "exec")
            compile_results[name] = "pass"
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_pressmachine_fusion)
    report_stream = io.StringIO()
    result = unittest.TextTestRunner(stream=report_stream, verbosity=1).run(suite)
    report = {
        "format": "pressmachine-toolkit-offline-validation-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "scope": "synthetic SDK mocks and Python compilation only",
        "compile": compile_results,
        "tests": {"run": result.testsRun, "failures": len(result.failures),
                  "errors": len(result.errors), "skipped": len(result.skipped),
                  "passed": result.wasSuccessful()},
        "hashes_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in paths},
        "schema_sha256": pm.SCHEMA_SHA256,
        "host_connection_attempted": False,
        "host_parameter_write_tested": False,
        "pixel_reflection_tested": False,
        "persistence_tested": False,
        "color_calibration_tested": False,
        "color_page_direct_api_tested": False,
        "fdb_tested": False,
    }
    pm.save_json(report, args.out)
    print(report_stream.getvalue(), end="")
    print("Saved offline validation: " + str(args.out))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
