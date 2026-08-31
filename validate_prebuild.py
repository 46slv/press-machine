#!/usr/bin/env python3
"""Deterministic prebuild validation for SatComp.

This is deliberately stronger than a text-only DCTL review:
1) run Python mathematical/color-contract tests;
2) compile and execute the DCTL through the native parity harness in tests;
3) run a standalone Clang syntax smoke check on the DCTL source.

The Clang checks do not replace DaVinci Resolve host validation.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    clang = shutil.which("clang")
    if not clang:
        print("ERROR: clang is required for the DCTL syntax gate.", file=sys.stderr)
        return 2
    run([
        clang,
        "-std=c11",
        "-fsyntax-only",
        "-include", str(ROOT / "tests" / "dctl_syntax_shim.h"),
        "-x", "c",
        str(ROOT / "SatComp_vNext.dctl"),
    ])
    print("SatComp prebuild validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
