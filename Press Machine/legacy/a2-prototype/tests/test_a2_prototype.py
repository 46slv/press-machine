"""Source-executed A2 scalar regressions; no DCTL/GPU/Resolve certification.

The gain helper is translated from the actual DCTL, not replaced by a Python
implementation. Expected curve values use the original source and the approved
subtractive A2 equation. The float32 check rounds scalar operations to binary32;
it does not emulate a GPU's fused operations, intrinsics, or denormal policy.
"""

from __future__ import annotations

import importlib.util
import math
import re
import runpy
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT.parent
SOURCE = (ROOT / "press_machine_a2_prototype.dctl").read_text(encoding="utf-8")
HARNESS = runpy.run_path(str(LEGACY / "v1.2.2/tests/test_neutral_density.py"))
ORIGINAL = HARNESS["ORIGINAL"]
PARTIAL = HARNESS["CORRECTED"]
OLD_PROBE = HARNESS["probe"]


def helper_body() -> str:
    start = SOURCE.index("__DEVICE__ float legacy_a2_gain(")
    opening = SOURCE.index("{", start)
    depth = 0
    for end in range(opening, len(SOURCE)):
        if SOURCE[end] == "{":
            depth += 1
        elif SOURCE[end] == "}":
            depth -= 1
            if depth == 0:
                return SOURCE[opening+1:end]
    raise AssertionError("Unclosed helper")


class F32(float):
    """Round each overloaded scalar operation, allowing gradual underflow."""

    def __new__(cls, value):
        value = float(value)
        try:
            value = struct.unpack("<f", struct.pack("<f", value))[0]
        except OverflowError:
            value = math.copysign(math.inf, value)
        return super().__new__(cls, value)

    def __add__(self, other): return F32(float(self) + float(other))
    def __radd__(self, other): return F32(float(other) + float(self))
    def __sub__(self, other): return F32(float(self) - float(other))
    def __rsub__(self, other): return F32(float(other) - float(self))
    def __mul__(self, other): return F32(float(self) * float(other))
    def __rmul__(self, other): return F32(float(other) * float(self))
    def __truediv__(self, other): return F32(float(self) / float(other))
    def __rtruediv__(self, other): return F32(float(other) / float(self))


def compile_gain(binary32: bool = False):
    lines = ["def gain(x, thr, kn, ratio):"]
    indent = 1
    for raw in helper_body().splitlines():
        line = re.sub(r"(?<=\d)f\b", "", raw.split("//", 1)[0].strip())
        if not line:
            continue
        if line == "}":
            indent -= 1
            continue
        condition = re.fullmatch(r"if \((.+)\) \{", line)
        if condition:
            lines.append("    " * indent + f"if {condition[1]}:")
            indent += 1
            continue
        assignment = re.fullmatch(r"float (\w+) = (.+);", line)
        returned = re.fullmatch(r"return (.+);", line)
        if assignment:
            statement = f"{assignment[1]} = {assignment[2]}"
        elif returned:
            statement = f"return {returned[1]}"
        else:
            raise AssertionError(f"Unsupported helper statement: {line}")
        lines.append("    " * indent + statement)
    if indent != 1:
        raise AssertionError("Unbalanced helper translation")
    cast = F32 if binary32 else float
    namespace = {
        "__builtins__": {},
        "_logf": lambda x: cast(math.log(float(x))),
        "clampf": lambda x, a, b: cast(max(a, min(b, x))),
    }
    exec(compile("\n".join(lines), "<actual DCTL A2 helper>", "exec"), namespace)
    function = namespace["gain"]
    if binary32:
        return lambda *args: F32(function(*(F32(v) for v in args)))
    return function


GAIN = compile_gain()


def pipeline(sat: float = 0.0, **settings):
    return OLD_PROBE(SOURCE, sat, legacy_a2_gain=GAIN, **settings)


def old_curve(x: float, ui: float, knee: float, ratio: float) -> float:
    return OLD_PROBE(ORIGINAL, x, Threshold=ui, Knee=knee,
                     Ratio=ratio, Sat_Density=0.0)["sat_out"]


def approved_curve(x: float, ui: float, knee: float, ratio: float) -> float:
    threshold, width = ui**3, max(knee, 1e-6)
    value = old_curve(x, ui, knee, ratio)
    if ratio > 1.0 and 0.0 < threshold < width and x < threshold:
        value -= old_curve(0.0, ui, knee, ratio) * (1.0-x/threshold)**2
    return value


class A2PrototypeTests(unittest.TestCase):
    def test_actual_helper_matches_approved_equation_in_each_branch(self):
        cases = (
            (0.25, 0.1, (0.0, 1e-12, 1e-6, .005, .01562499, .015625,
                         .01562501, .03, .11562499, .115625, .11562501, .8)),
            (0.5, 0.1, (0.0, .02499999, .025, .02500001, .075, .125, .225, .8)),
            (0.25, .015625, (0.0, 1e-12, .0078125, .015625, .03)),
            (0.0, .1, (0.0, 1e-12, .01, .1, .2)),
            (.005, 0.0, (0.0, 1e-12, .0000000625, .000000125, .000001)),
        )
        for ui, knee, points in cases:
            for x in points:
                with self.subTest(ui=ui, knee=knee, x=x):
                    actual = x * GAIN(x, ui**3, max(knee, 1e-6), 4.0)
                    self.assertAlmostEqual(actual, approved_curve(x, ui, knee, 4.0),
                                           delta=4e-14)

    def test_original_neutral_and_near_neutral_regressions_are_fixed(self):
        old = OLD_PROBE(ORIGINAL, 0.0)
        self.assertAlmostEqual(old["luma_final"], .177866896920, places=11)
        self.assertGreater(old["sat_out"], .00599)
        neutral = pipeline()
        self.assertEqual(neutral["sat_out"], 0.0)
        self.assertEqual(neutral["chroma_final"], 0.0)
        self.assertEqual(neutral["luma_final"], .18)
        for sat in (1e-12, .5e-6, 1e-6, 1.0001e-6):
            with self.subTest(sat=sat):
                result = pipeline(sat)
                self.assertGreater(result["chroma_final"], 0.0)
                self.assertLessEqual(result["chroma_final"], 1.5 * sat)
                self.assertAlmostEqual(result["sat_out"], result["chroma_final"], places=17)

    def test_old_guard_has_no_chroma_or_density_jump(self):
        left, right = .999999e-6, 1.000001e-6
        old_left, old_right = OLD_PROBE(PARTIAL, left), OLD_PROBE(PARTIAL, right)
        self.assertGreater(old_left["luma_final"]-old_right["luma_final"], .002)
        for settings in ({}, dict(Pre_Saturation=3.0, Makeup=4.0, Density_SatBoost=1.0)):
            with self.subTest(settings=settings):
                a, b = pipeline(left, **settings), pipeline(right, **settings)
                self.assertLess(abs(a["luma_final"]-b["luma_final"]), 1e-10)
                self.assertLess(abs(a["chroma_final"]-b["chroma_final"]), 1e-9)

    def test_analytic_origin_limits_and_knee_crossing(self):
        threshold, knee, ratio = .015625, .1, 4.0
        self.assertEqual(GAIN(0.0, threshold, knee, ratio), 1.5-.5*(threshold/knee)**3)
        self.assertAlmostEqual(GAIN(0.0, 0.0, knee, ratio),
                               .5*(1+1/(1+math.log(ratio))), places=15)
        self.assertEqual(GAIN(0.0, threshold, threshold, ratio), 1.0)
        self.assertEqual(GAIN(0.0, .125, .1, ratio), 1.0)
        for k in (threshold*(1-1e-9), threshold, threshold*(1+1e-9)):
            self.assertAlmostEqual(GAIN(threshold/2, threshold, k, ratio),
                                   GAIN(threshold/2, threshold, threshold, ratio), delta=2e-9)

    def test_threshold_value_and_retained_one_sided_slopes(self):
        threshold, knee, ratio = .015625, .1, 4.0
        f = lambda x: x*GAIN(x, threshold, knee, ratio)
        step = threshold*1e-6
        self.assertEqual(f(threshold), threshold)
        self.assertAlmostEqual((f(threshold)-f(threshold-step))/step, .5, delta=2e-6)
        self.assertAlmostEqual((f(threshold+step)-f(threshold))/step,
                               .5*(1+1/(1+math.log(ratio))), delta=2e-6)
        for boundary in (.025, .225):
            f = lambda x: x*GAIN(x, .125, .1, ratio)
            self.assertLess(abs(f(boundary+1e-10)-f(boundary-1e-10)), 3e-10)

    def test_ratio_one_and_pre_makeup_zero(self):
        for sat in (0.0, 1e-9, .12):
            with self.subTest(sat=sat):
                bypass = pipeline(sat, Ratio=1.0, Sat_Density=0.0)
                self.assertEqual(bypass["chroma_final"], sat)
                self.assertEqual(bypass["luma_final"], .18)
                for settings in (dict(Pre_Saturation=0.0), dict(Makeup=0.0)):
                    value = pipeline(sat, **settings)
                    self.assertEqual(value["sat_out"], 0.0)
                    self.assertEqual(value["chroma_final"], 0.0)
                    self.assertEqual(value["luma_final"], .18)
        value = pipeline(.12, Makeup=0.0, Dynamic_Density=1.0)
        old = OLD_PROBE(ORIGINAL, .12, Makeup=0.0, Dynamic_Density=1.0)
        self.assertEqual(value["luma_final"], old["luma_final"])

    def test_nonproblematic_creative_paths_are_retained(self):
        for sat, ui in ((.075, .5), (.03, .25), (.8, .25)):
            with self.subTest(sat=sat, ui=ui):
                settings = dict(Threshold=ui, Makeup=1.6, Dynamic_Density=.4,
                                Luma_Density=2.0, Density_Comp=.2, Density_SatBoost=.5)
                old, new = OLD_PROBE(ORIGINAL, sat, **settings), pipeline(sat, **settings)
                for key in ("sat_pre", "sat_out", "luma_working", "luma_final", "chroma_final"):
                    self.assertAlmostEqual(old[key], new[key], delta=2e-13)

    def test_density_compensation_and_boost_stage_order(self):
        settings = dict(Dynamic_Density=.6, Luma_Density=2.0, Luma_Density_Power=1.5)
        neutral = pipeline(**settings)
        baseline = pipeline(Sat_Density=0.0, **settings)
        self.assertEqual(neutral["luma_final"], baseline["luma_final"])
        self.assertLess(neutral["luma_final"], 0.0)  # Preserve Luma Mix extrapolation.
        compensated = pipeline(.005, Density_Comp=1.0, **settings)
        baseline = pipeline(.005, Sat_Density=0.0, **settings)
        self.assertEqual(compensated["luma_final"], baseline["luma_final"])
        normal, boosted = pipeline(.005), pipeline(.005, Density_SatBoost=1.0)
        self.assertEqual(normal["luma_final"], boosted["luma_final"])
        self.assertEqual(boosted["chroma_final"], 2*normal["chroma_final"])

    def test_nonnegative_finite_gain_in_binary32_edge_probes(self):
        gain32 = compile_gain(binary32=True)
        for ui, knee in ((.25, .1), (.5, .1), (.25, .015625), (0.0, .1), (.005, 0.0)):
            threshold, width = F32(F32(ui)**3), max(F32(knee), F32(1e-6))
            points = {0.0, 2**-149, 2**-126, 1e-20, 1e-6, .005, 1.0, 1e10}
            for boundary in (threshold, max(0.0, threshold-width), threshold+width, F32(1e-6)):
                bits = struct.unpack("<I", struct.pack("<f", boundary))[0]
                for offset in (-1, 0, 1):
                    if bits+offset >= 0:
                        points.add(struct.unpack("<f", struct.pack("<I", bits+offset))[0])
            for x in points:
                with self.subTest(ui=ui, knee=knee, x=x):
                    value = gain32(x, threshold, width, 20.0)
                    self.assertTrue(math.isfinite(value))
                    self.assertGreaterEqual(value, 0.0)
                    self.assertLessEqual(value, 1.500001)

    def test_payload_changes_only_approved_sections(self):
        def section(source, a, b):
            return source[source.index(a):source.index(b, source.index(a))]

        restored = SOURCE
        begin = restored.index("// A2 gain: x >= 0")
        end = restored.index("// ====================================================================\n// MAIN TRANSFORM", begin)
        restored = restored[:begin]+restored[end:]
        new = section(restored, "    // 3. Saturation Compression", "    // 4. Luma Density")
        old = section(ORIGINAL, "    // 3. Saturation Compression", "    // 4. Luma Density")
        restored = restored.replace(new, old, 1)
        begin = restored.index("    // Finite gain replaces")
        end = restored.index("    if (Density_SatBoost", begin)
        old_line = section(ORIGINAL, "    float3 chroma_final", "    if (Density_SatBoost")
        restored = restored[:begin]+old_line+restored[end:]
        new_graph = section(restored, "            float g_thr", "            // Y axis:")
        old_graph = section(ORIGINAL, "            float g_sat_out", "            // Y axis:")
        restored = restored.replace(new_graph, old_graph, 1)
        marker = "// ===================================================================="
        self.assertEqual(restored[restored.index(marker):], ORIGINAL[ORIGINAL.index(marker):])
        self.assertNotIn("sat_for_density", SOURCE)
        self.assertNotIn("sat_out / sat_in", SOURCE)

    def test_graph_calls_same_curve_with_retained_mapping(self):
        self.assertIn("float sat_gain = legacy_a2_gain(sat_pre, thr, kn, Ratio);", SOURCE)
        self.assertIn("float g_sat_out = plot_x * legacy_a2_gain(plot_x, g_thr, g_kn, Ratio);", SOURCE)
        self.assertEqual(SOURCE.count("legacy_a2_gain("), 3)  # definition + two uses
        self.assertIn("g_sat_out * Makeup / 2.0f", SOURCE)
        self.assertIn("_fabs(gx - gy)", SOURCE)

    def test_retained_logc4_and_graph_contracts(self):
        path = LEGACY / "v1.2.1/tests/test_v1_2_1_contract.py"
        spec = importlib.util.spec_from_file_location("retained_v121", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.SOURCE = SOURCE
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 5)
        self.assertEqual(result.errors+result.failures, [])


if __name__ == "__main__":
    unittest.main()
