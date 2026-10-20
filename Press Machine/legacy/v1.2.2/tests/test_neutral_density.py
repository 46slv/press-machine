"""Focused scalar arithmetic/source tests; no GPU or DCTL host certification.

Execute the actual DCTL statements from Pre-Saturation through reconstruction
using Python doubles. Only this small C-like subset is translated; unsupported
statements fail the harness. Chroma is represented by its nonnegative magnitude
because this block only scales the original vector (or replaces it with zero).
"""

from __future__ import annotations

import importlib.util
import math
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / "v1.2.1"
ORIGINAL = (BASE / "press_machine_v1_2_1.dctl").read_text(encoding="utf-8")
CORRECTED = (ROOT / "press_machine_v1_2_2.dctl").read_text(encoding="utf-8")

GUARD = """        // Match reconstruction: the legacy knee can report saturation
        // even when the input chroma is too small to reconstruct.
        float sat_for_density = (sat_in > 1e-6f) ? sat_out : 0.0f;
"""


def scalar_program(source: str) -> str:
    block = source.split("    // 1. Pre-Saturation Boost\n", 1)[1]
    block = block.split("    float3 color_out =", 1)[0]
    translated = []
    indent = 0
    for raw in block.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        line = re.sub(r"(?<=\d)f\b", "", line)
        if line == "}":
            indent -= 1
            if indent < 0:
                raise AssertionError("Unbalanced source block")
            continue
        condition = re.fullmatch(r"if \((.+)\) \{", line)
        if condition:
            translated.append("    " * indent + f"if {condition[1]}:")
            indent += 1
            continue
        assignment = re.fullmatch(r"(?:float3?\s+)?(\w+)\s*(=|\*=)\s*(.+);", line)
        if not assignment:
            raise AssertionError(f"Unsupported DCTL statement: {line}")
        name, operator, expression = assignment.groups()
        if "?" in expression:
            condition, branches = expression.split("?", 1)
            yes, no = branches.split(":", 1)
            expression = f"({yes} if {condition} else {no})"
        translated.append("    " * indent + f"{name} {operator} {expression}")
    if indent:
        raise AssertionError("Unclosed source block")
    return "\n".join(translated)


def zero_vector(x: float, y: float, z: float) -> float:
    if (x, y, z) != (0.0, 0.0, 0.0):
        raise AssertionError("Only the reconstruction zero vector is supported")
    return 0.0


def probe(source: str, sat_in: float = 0.0, **controls: float) -> dict:
    values = dict(
        sat_in=sat_in,
        chroma_orig=sat_in,
        luma_orig=0.18,
        Pre_Saturation=1.0,
        Dynamic_Density=0.0,
        Threshold=0.25,
        Ratio=4.0,
        Knee=0.1,
        Makeup=1.0,
        Luma_Density=0.0,
        Luma_Density_Power=1.5,
        Sat_Density=1.0,
        Density_Comp=0.0,
        Density_SatBoost=0.0,
        _fmaxf=max,
        _powf=pow,
        _logf=math.log,
        clampf=lambda x, a, b: max(a, min(b, x)),
        mixf=lambda a, b, t: a * (1.0 - t) + b * t,
        make_float3=zero_vector,
    )
    values.update(controls)
    exec(compile(scalar_program(source), "<DCTL scalar block>", "exec"),
         {"__builtins__": {}}, values)
    return values


class NeutralDensityTests(unittest.TestCase):
    def test_original_regression_and_corrected_neutral(self) -> None:
        old, new = probe(ORIGINAL), probe(CORRECTED)
        self.assertAlmostEqual(old["sat_out"], 0.005996, places=6)
        self.assertAlmostEqual(old["luma_final"], 0.177867, places=6)
        self.assertEqual(old["chroma_final"], 0.0)
        self.assertEqual(new["sat_out"], old["sat_out"])
        self.assertEqual(new["chroma_final"], 0.0)
        self.assertEqual(new["luma_final"], 0.18)

    def test_near_neutral_through_inclusive_reconstruction_guard(self) -> None:
        for sat in (0.0, 0.5e-6, 1e-6):
            with self.subTest(sat=sat):
                old = probe(ORIGINAL, sat, Pre_Saturation=3.0, Makeup=2.0)
                new = probe(CORRECTED, sat, Pre_Saturation=3.0, Makeup=2.0)
                self.assertLess(old["luma_final"], 0.18)
                self.assertEqual(new["luma_final"], 0.18)
                self.assertEqual(new["chroma_final"], 0.0)

    def test_dynamic_and_luma_density_remain_intentional(self) -> None:
        # Luma Mix 2 deliberately extrapolates; do not turn this into a bypass.
        for sat in (0.0, 0.5e-6, 1e-6):
            with self.subTest(sat=sat):
                settings = dict(Dynamic_Density=0.6, Luma_Density=2.0,
                                Luma_Density_Power=1.5, Makeup=3.0,
                                Density_SatBoost=0.5, Density_Comp=0.4)
                baseline = probe(ORIGINAL, sat, Sat_Density=0.0, **settings)
                actual = probe(CORRECTED, sat, **settings)
                self.assertEqual(actual["luma_final"], baseline["luma_final"])
                self.assertEqual(actual["luma_working"], baseline["luma_working"])
                self.assertNotEqual(actual["luma_final"], 0.18)
                self.assertEqual(actual["chroma_final"], 0.0)

    def test_nearby_non_neutral_and_creative_response_are_unchanged(self) -> None:
        # The first sample records the known residual knee/guard discontinuity.
        for sat in (1.0001e-6, 0.015625, 0.12, 0.8):
            with self.subTest(sat=sat):
                settings = dict(Dynamic_Density=0.4, Makeup=1.6,
                                Luma_Density=0.3, Density_Comp=0.2,
                                Density_SatBoost=0.5)
                old = probe(ORIGINAL, sat, **settings)
                new = probe(CORRECTED, sat, **settings)
                for name in ("sat_pre", "sat_out", "chroma_final", "luma_final"):
                    self.assertEqual(new[name], old[name], name)
        above_guard = probe(CORRECTED, 1.0001e-6)
        self.assertGreater(above_guard["chroma_final"], 0.00599)
        self.assertLess(above_guard["luma_final"], 0.178)

    def test_density_no_op_cases(self) -> None:
        for settings in (dict(Sat_Density=0.0), dict(Density_Comp=1.0),
                         dict(Makeup=0.0), dict(Ratio=1.0, sat_in=0.0),
                         dict(Knee=0.0), dict(Threshold=0.8)):
            with self.subTest(settings=settings):
                old, new = probe(ORIGINAL, **settings), probe(CORRECTED, **settings)
                self.assertEqual(new["luma_final"], old["luma_final"])
                self.assertEqual(new["luma_final"], 0.18)
                self.assertEqual(new["chroma_final"], old["chroma_final"])
        neutral_controls = probe(CORRECTED, 0.12, Ratio=1.0, Sat_Density=0.0)
        self.assertEqual(neutral_controls["luma_final"], 0.18)
        self.assertEqual(neutral_controls["chroma_final"], 0.12)

    def test_payload_diff_is_only_the_density_guard(self) -> None:
        # Preserve every non-header byte of equations/UI/graph except this fix.
        def payload(source: str) -> str:
            return source[source.index("// ===================================================================="):]

        restored = CORRECTED.replace(GUARD, "", 1).replace(
            "1.0f + sat_for_density * Sat_Density * 2.0f",
            "1.0f + sat_out * Sat_Density * 2.0f", 1)
        self.assertIn(GUARD, CORRECTED)
        self.assertEqual(payload(restored), payload(ORIGINAL))

    def test_retained_v1_2_1_contracts_against_new_variant(self) -> None:
        path = BASE / "tests/test_v1_2_1_contract.py"
        spec = importlib.util.spec_from_file_location("retained_v121", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.SOURCE = CORRECTED
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 5)
        self.assertEqual(result.errors + result.failures, [])


if __name__ == "__main__":
    unittest.main()
