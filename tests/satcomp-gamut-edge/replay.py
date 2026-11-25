"""Rebuild both complete DCTLs as native Windows CPU test libraries."""
from argparse import ArgumentParser
import csv
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default="g++", help="Path to MinGW-w64 g++")
    parser.add_argument("--out", required=True, type=Path, help="New scratch directory")
    args = parser.parse_args()
    cxx = shutil.which(args.cxx)
    if sys.platform != "win32" or not cxx:
        parser.error("Requires Windows and MinGW-w64 g++")
    out = args.out.resolve()
    root = Path(__file__).resolve().parent
    env = {**os.environ, "SATCOMP_REPLAY_OUT": str(out), "SATCOMP_REPLAY_DLL_DIR": str(Path(cxx).parent),
           "PATH": str(Path(cxx).parent) + os.pathsep + os.environ.get("PATH", ""),
           "TEMP": str(out), "TMP": str(out), "PYTHONDONTWRITEBYTECODE": "1"}
    sources = (
        ("baseline", root / "fixtures/PressMachine_Comp_Color_Normalized_TEST.dctl", "db784f2fd24c7e34df9a33f56e1f93ba202df3fccbd924c17a0c92f5b092bb75"),
        ("candidate", root.parents[1] / "adapters/dctl/candidates/PressMachine_Comp_Color_Normalized_GamutEdge_20261125.dctl", "fbee7172303d8f498f0ff3f6ad0161c2bd6baf376867dc724932cf5371133c35"),
    )
    for lane, path, sha in sources:
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            raise ValueError(f"Wrong source bytes: {lane}")
    out.mkdir(parents=True, exist_ok=False)
    for lane, path, _ in sources:
        subprocess.run([cxx, "-std=c++17", "-O2", "-fno-fast-math", "-ffp-contract=off", "-shared",
                        f'-DDCTL_FILE="{path.as_posix()}"', "-o", str(out / f"{lane}.dll"),
                        str(root / "cpu_adapter.cpp")], env=env, check=True)
    for name, expected, *cmd in (
        ("RED", 1, "test_conversion.py", "baseline"),
        ("GREEN", 0, "test_conversion.py", "candidate"),
        ("edges", 0, "test_edges.py"),
        ("legacy-regression", 0, "legacy_replay.py"),
    ):
        p = subprocess.run([sys.executable, "-B", str(root / cmd[0]), *cmd[1:]],
                           env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, encoding="utf-8", errors="replace")
        (out / (name + ".log")).write_text(f"{p.stdout}\nexit={p.returncode}\n", encoding="utf-8")
        if p.returncode != expected:
            raise RuntimeError(f"{name}: expected {expected}, got {p.returncode}; see {out}")
        if name == "RED" and not all("FAIL " + s in p.stdout for s in (
            "same-gamut extreme transfer-only", "finite encoded range", "finite decoded range"
        )):
            raise RuntimeError("RED did not reproduce the intended failures")
        print(name, "exit", p.returncode)
    with (out / "edge-metrics.csv").open(newline="", encoding="utf-8") as fh:
        rows = len(list(csv.reader(fh))) - 1
    if rows != 180:
        raise RuntimeError(f"expected 180 edge-metric rows, got {rows}")
    print("Verified 180 metric rows.")

if __name__ == "__main__":
    main()
