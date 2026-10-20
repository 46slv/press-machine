"""Small arithmetic and source-contract regressions for legacy DCTL v1.2.1.

The numerical helpers below mirror the published ARRI LogC4 reference equations.
The source checks tie those probes to the DCTL text; they do not replace a DCTL
compiler or a DaVinci Resolve integration test.
"""

from __future__ import annotations

import math
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DCTL_PATH = ROOT / "press_machine_v1_2_1.dctl"
ORIGINAL_PATH = ROOT.parent / "press_machine_v1_2.dctl"
SOURCE = DCTL_PATH.read_text(encoding="utf-8")
ORIGINAL_SOURCE = ORIGINAL_PATH.read_text(encoding="utf-8")


def arri_logc4_constants() -> tuple[float, float, float, float, float]:
    a = (2.0**18 - 16.0) / 117.45
    b = (1023.0 - 95.0) / 1023.0
    c = 95.0 / 1023.0
    toe_slope = (7.0 * math.log(2.0) * 2.0 ** (7.0 - 14.0 * c / b)) / (a * b)
    linear_cut = (2.0 ** (14.0 * (-c / b) + 6.0) - 64.0) / a
    return a, b, c, toe_slope, linear_cut


def arri_logc4_decode(code: float) -> float:
    a, b, c, toe_slope, linear_cut = arri_logc4_constants()
    if code < 0.0:
        return code * toe_slope + linear_cut
    p = 14.0 * (code - c) / b + 6.0
    return (2.0**p - 64.0) / a


def arri_logc4_encode(linear: float) -> float:
    a, b, c, toe_slope, linear_cut = arri_logc4_constants()
    if linear < linear_cut:
        return (linear - linear_cut) / toe_slope
    return (math.log2(a * linear + 64.0) - 6.0) / 14.0 * b + c


def legacy_v1_2_logc4_decode(code: float) -> float:
    a = (2.0**18 - 16.0) / 117.45
    b = (1024.0 - 121.0) / (1024.0 - 12.0)
    c = 12.0 / 1024.0
    d = 155.0 / 1024.0
    return (2.0 ** ((code - d) / c) - b) / a * 100.0 / 18.0 - 0.01 / 0.18


def legacy_v1_2_logc4_encode(linear: float) -> float:
    a = (2.0**18 - 16.0) / 117.45
    b = (1024.0 - 121.0) / (1024.0 - 12.0)
    c = 12.0 / 1024.0
    d = 155.0 / 1024.0
    s = (linear * 0.18 + 0.01) * a / 100.0
    return math.log2(s + b) * c + d


def function_body(name: str) -> str:
    match = re.search(
        rf"__DEVICE__\s+float\s+{re.escape(name)}\s*\(\s*float\s+x\s*\)\s*\{{",
        SOURCE,
    )
    if not match:
        raise AssertionError(f"DCTL function not found: {name}")
    start = SOURCE.find("{", match.start())
    depth = 0
    for index in range(start, len(SOURCE)):
        if SOURCE[index] == "{":
            depth += 1
        elif SOURCE[index] == "}":
            depth -= 1
            if depth == 0:
                return SOURCE[start + 1 : index]
    raise AssertionError(f"Unclosed DCTL function: {name}")


class LogC4ContractTests(unittest.TestCase):
    def test_v1_2_failure_is_reproduced_and_v1_2_1_corrects_it(self) -> None:
        self.assertIn("1024.0f - 121.0f", ORIGINAL_SOURCE)
        self.assertIn("100.0f / 18.0f", ORIGINAL_SOURCE)
        self.assertIn("_fabs((gx * 0.5f) - gy)", ORIGINAL_SOURCE)

        code_18_gray = arri_logc4_encode(0.18)
        old_code = legacy_v1_2_logc4_encode(0.18)
        old_roundtrip = legacy_v1_2_logc4_decode(old_code)
        self.assertAlmostEqual(code_18_gray, 0.2783958365, places=9)
        self.assertAlmostEqual(old_code, 0.1616632499, places=9)
        self.assertAlmostEqual(old_roundtrip, -0.0532, places=9)
        self.assertNotAlmostEqual(old_roundtrip, 0.18, places=2)

        self.assertAlmostEqual(
            arri_logc4_decode(arri_logc4_encode(0.18)), 0.18, places=12
        )

    def test_dctl_decoder_and_encoder_keep_reference_constants_and_toes(self) -> None:
        decoder = function_body("logc4_to_lin")
        encoder = function_body("lin_to_logc4")

        for body in (decoder, encoder):
            self.assertIn("(1023.0f - 95.0f) / 1023.0f", body)
            self.assertIn("95.0f / 1023.0f", body)
            self.assertIn("linear_cut", body)
            self.assertIn("toe_slope", body)
        self.assertRegex(decoder, r"if\s*\(\s*x\s*<\s*0\.0f\s*\)")
        self.assertIn("return x * toe_slope + linear_cut;", decoder)
        self.assertIn(
            "const float linear_cut = (_powf(2.0f, 14.0f * (-c / b) + 6.0f) - 64.0f) / a;",
            decoder,
        )
        self.assertIn("return (_powf(2.0f, p) - 64.0f) / a;", decoder)
        self.assertIn("if (x < linear_cut)", encoder)
        self.assertIn("return (x - linear_cut) / toe_slope;", encoder)
        self.assertIn(
            "return (_log2f(a * x + 64.0f) - 6.0f) / 14.0f * b + c;", encoder
        )

    def test_known_logc4_anchors(self) -> None:
        a, b, c, toe_slope, linear_cut = arri_logc4_constants()
        code_18_gray = arri_logc4_encode(0.18)

        self.assertAlmostEqual(code_18_gray, 0.2783958365, places=9)
        self.assertAlmostEqual(arri_logc4_decode(code_18_gray), 0.18, places=12)
        self.assertAlmostEqual(arri_logc4_decode(0.0), linear_cut, places=12)
        self.assertAlmostEqual(arri_logc4_encode(linear_cut), 0.0, places=12)
        self.assertGreater(toe_slope, 0.0)
        self.assertGreater(a, 0.0)
        self.assertGreater(b, 0.0)
        self.assertGreater(c, 0.0)

    def test_roundtrip_includes_negative_toe_zero_gray_and_highlight(self) -> None:
        _, _, _, _, linear_cut = arri_logc4_constants()
        linear_samples = [-1.0, -0.01, linear_cut, 0.0, 0.18, 1.0, 10.0]
        for linear in linear_samples:
            with self.subTest(linear=linear):
                self.assertAlmostEqual(
                    arri_logc4_decode(arri_logc4_encode(linear)),
                    linear,
                    delta=2e-11 * max(1.0, abs(linear)),
                )

        code_samples = [-0.1, -0.01, 0.0, arri_logc4_encode(0.18), 0.5, 1.0]
        for code in code_samples:
            with self.subTest(code=code):
                self.assertAlmostEqual(
                    arri_logc4_encode(arri_logc4_decode(code)),
                    code,
                    delta=2e-11 * max(1.0, abs(code)),
                )

    def test_graph_identity_line_uses_normalized_axes(self) -> None:
        self.assertIn("_fabs((gx * 0.5f) - gy)", ORIGINAL_SOURCE)
        self.assertRegex(SOURCE, r"_fabs\s*\(\s*gx\s*-\s*gy\s*\)")
        self.assertNotRegex(SOURCE, r"_fabs\s*\(\s*\(\s*gx\s*\*\s*0\.5f\s*\)")


if __name__ == "__main__":
    unittest.main()
