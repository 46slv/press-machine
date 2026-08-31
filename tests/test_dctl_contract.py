from pathlib import Path
import re
import unittest


DCTL = (Path(__file__).parents[1] / "SatComp_vNext.dctl").read_text()


class DctlContractTests(unittest.TestCase):
    def test_required_user_controls_exist(self):
        for name in (
            "p_threshold", "p_ratio", "p_knee", "p_bypass",
            "p_input_gamut", "p_input_transfer", "p_output_gamut", "p_output_transfer",
        ):
            self.assertIn(f"DEFINE_UI_PARAMS({name},", DCTL)

    def test_core_is_high_saturation_compressor(self):
        self.assertIn("satcomp_transfer", DCTL)
        self.assertIn("threshold + (sat - threshold) / ratio", DCTL)
        self.assertIn("d*d", DCTL)
        self.assertIn("sat_in = chroma / lab.x", DCTL)

    def test_no_hidden_gamut_clip(self):
        self.assertNotIn("_saturatef", DCTL)
        self.assertNotIn("_clampf", DCTL)
        self.assertNotRegex(DCTL, r"_fminf\s*\([^\n]*1\.0f")

    def test_color_spaces_and_transfers_are_explicit(self):
        for token in (
            "Rec.709", "Rec.2020", "DaVinci Wide Gamut", "ACEScg AP1",
            "sRGB", "Rec.709 OETF", "Gamma 2.4", "DaVinci Intermediate", "ACEScct",
        ):
            self.assertIn(token, DCTL)

    def test_exact_identity_fast_paths_exist(self):
        self.assertIn("if (p_bypass && same_encoding) return original;", DCTL)
        self.assertIn("if (same_encoding && p_ratio <= 1.0000001f) return original;", DCTL)
        self.assertIn("if (!changed && same_encoding) return original;", DCTL)

    def test_no_ceiling_parameter_in_v1(self):
        self.assertNotIn("p_ceiling", DCTL.lower())


if __name__ == "__main__":
    unittest.main()
