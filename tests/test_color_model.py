import math
import unittest

from color_model import (
    ACESCG,
    ACESCCT,
    DWG_INTERMEDIATE,
    LINEAR_ACESCG,
    LINEAR_DWG,
    LINEAR_REC2020,
    LINEAR_REC709,
    REC709_GAMMA24,
    REC709_OETF,
    SRGB,
    apply_satcomp_encoded,
    encoded_rgb_to_xyz_d65,
    xyz_d65_to_encoded_rgb,
    ACES_WHITE,
    D65,
    DWG,
    REC2020,
    REC709,
    acescct_decode_channel,
    acescct_encode_channel,
    bradford_adaptation_matrix,
    compress_oklab_saturation,
    davinci_intermediate_decode_channel,
    davinci_intermediate_encode_channel,
    linear_rgb_to_xyz_d65,
    oklab_chroma,
    oklab_hue,
    oklab_saturation,
    oklab_to_xyz_d65,
    rec709_decode_channel,
    rec709_encode_channel,
    srgb_decode_channel,
    srgb_encode_channel,
    xyz_d65_to_linear_rgb,
    xyz_d65_to_oklab,
)
from satcomp_transfer import compress_saturation


def assert_vec_near(test, a, b, tol=2e-9):
    for i, (x, y) in enumerate(zip(a, b)):
        test.assertAlmostEqual(x, y, delta=tol, msg=f"component {i}: {x} != {y}")


class ColorModelTests(unittest.TestCase):
    def test_dwg_matrix_matches_blackmagic_published_matrix(self):
        expected = (
            (0.70062239, 0.14877482, 0.10105872),
            (0.27411851, 0.87363190, -0.14775041),
            (-0.09896291, -0.13789533, 1.32591599),
        )
        for actual_row, expected_row in zip(DWG.rgb_to_xyz_native, expected):
            assert_vec_near(self, actual_row, expected_row, tol=8e-8)

    def test_acescg_matrix_matches_reference(self):
        expected = (
            (0.662454181109, 0.134004206456, 0.156187687005),
            (0.272228716781, 0.674081765811, 0.053689517408),
            (-0.005574649490, 0.004060733529, 1.010339100313),
        )
        for actual_row, expected_row in zip(ACESCG.rgb_to_xyz_native, expected):
            assert_vec_near(self, actual_row, expected_row, tol=3e-12)

    def test_aces_white_to_d65_bradford_matches_reference(self):
        expected = (
            (0.987224008703, -0.006113228607, 0.015953288336),
            (-0.007598371812, 1.001861484740, 0.005330035791),
            (0.003072577059, -0.005095961511, 1.081680603066),
        )
        actual = bradford_adaptation_matrix(ACES_WHITE, D65)
        for actual_row, expected_row in zip(actual, expected):
            assert_vec_near(self, actual_row, expected_row, tol=2e-9)

    def test_linear_rgb_xyz_roundtrip_preserves_extended_range(self):
        samples = [
            (0.18, 0.18, 0.18),
            (1.2, 0.2, -0.05),
            (-0.1, 0.3, 2.0),
        ]
        for space in (REC709, REC2020, DWG, ACESCG):
            for rgb in samples:
                with self.subTest(space=space.name, rgb=rgb):
                    xyz = linear_rgb_to_xyz_d65(rgb, space)
                    rt = xyz_d65_to_linear_rgb(xyz, space)
                    assert_vec_near(self, rgb, rt, tol=2e-9)

    def test_same_xyz_produces_same_oklab_and_saturation_from_all_gamuts(self):
        xyz = (0.31, 0.22, 0.08)
        direct_lab = xyz_d65_to_oklab(xyz)
        direct_s = oklab_saturation(direct_lab)
        for space in (REC709, REC2020, DWG, ACESCG):
            rgb = xyz_d65_to_linear_rgb(xyz, space)
            recovered_xyz = linear_rgb_to_xyz_d65(rgb, space)
            lab = xyz_d65_to_oklab(recovered_xyz)
            assert_vec_near(self, lab, direct_lab, tol=2e-9)
            self.assertAlmostEqual(oklab_saturation(lab), direct_s, delta=2e-9)

    def test_oklab_roundtrip(self):
        cases = [
            (0.18, 0.18, 0.18),
            (0.31, 0.22, 0.08),
            (0.9, 0.5, 0.2),
            (0.1, 0.2, 0.7),
        ]
        for xyz in cases:
            lab = xyz_d65_to_oklab(xyz)
            rt = oklab_to_xyz_d65(lab)
            assert_vec_near(self, xyz, rt, tol=2e-9)

    def test_oklab_saturation_is_exposure_scale_invariant(self):
        xyz = (0.31, 0.22, 0.08)
        baseline = oklab_saturation(xyz_d65_to_oklab(xyz))
        for scale in (0.01, 0.1, 0.5, 2.0, 16.0, 100.0):
            scaled = tuple(v * scale for v in xyz)
            s = oklab_saturation(xyz_d65_to_oklab(scaled))
            self.assertAlmostEqual(s, baseline, delta=2e-9)

    def test_compression_preserves_oklab_lightness_and_hue(self):
        lab = xyz_d65_to_oklab((0.31, 0.22, 0.08))
        s_in = oklab_saturation(lab)
        transfer = lambda s: compress_saturation(s, threshold=s_in * 0.6, ratio=3.0, knee=s_in * 0.1)
        out = compress_oklab_saturation(lab, transfer)
        self.assertAlmostEqual(out[0], lab[0], delta=1e-15)
        self.assertAlmostEqual(oklab_hue(out), oklab_hue(lab), delta=1e-12)
        self.assertLess(oklab_saturation(out), s_in)

    def test_below_threshold_full_color_path_is_identity(self):
        xyz = (0.20, 0.205, 0.19)
        lab = xyz_d65_to_oklab(xyz)
        s = oklab_saturation(lab)
        transfer = lambda x: compress_saturation(x, threshold=s + 0.2, ratio=4.0, knee=0.1)
        out_lab = compress_oklab_saturation(lab, transfer)
        out_xyz = oklab_to_xyz_d65(out_lab)
        assert_vec_near(self, xyz, out_xyz, tol=2e-9)

    def test_neutral_axis_remains_neutral(self):
        for y in (1e-6, 0.001, 0.18, 1.0, 16.0):
            # D65 neutral XYZ normalized to Y.
            xw = D65[0] / D65[1] * y
            zw = (1 - D65[0] - D65[1]) / D65[1] * y
            lab = xyz_d65_to_oklab((xw, y, zw))
            self.assertLess(oklab_chroma(lab), 2e-8)
            out = compress_oklab_saturation(
                lab,
                lambda s: compress_saturation(s, threshold=0.2, ratio=8.0, knee=0.1),
            )
            self.assertLess(oklab_chroma(out), 2e-8)

    def test_transfer_function_roundtrips(self):
        for encode, decode, values in (
            (srgb_encode_channel, srgb_decode_channel, (-0.1, 0.0, 0.003, 0.18, 1.0, 2.0)),
            (rec709_encode_channel, rec709_decode_channel, (-0.1, 0.0, 0.01, 0.18, 1.0, 2.0)),
            (davinci_intermediate_encode_channel, davinci_intermediate_decode_channel, (-0.01, 0.0, 0.18, 1.0, 10.0, 100.0)),
            (acescct_encode_channel, acescct_decode_channel, (-0.01, 0.0, 0.0078125, 0.18, 1.0, 16.0)),
        ):
            for x in values:
                with self.subTest(encode=encode.__name__, x=x):
                    self.assertAlmostEqual(decode(encode(x)), x, delta=3e-8)

    def test_cross_encoding_satcomp_decision_is_invariant(self):
        xyz = (0.31, 0.22, 0.08)
        encodings = (
            LINEAR_REC709, SRGB, REC709_OETF, REC709_GAMMA24,
            LINEAR_REC2020, LINEAR_DWG, DWG_INTERMEDIATE, LINEAR_ACESCG, ACESCCT,
        )
        reference = None
        for encoding in encodings:
            rgb = xyz_d65_to_encoded_rgb(xyz, encoding)
            result = apply_satcomp_encoded(
                rgb, encoding, encoding,
                threshold=0.20, ratio=3.0, knee=0.08,
            )
            out_xyz = encoded_rgb_to_xyz_d65(result.rgb, encoding)
            if reference is None:
                reference = (result.saturation_in, result.saturation_out, out_xyz)
            else:
                self.assertAlmostEqual(result.saturation_in, reference[0], delta=3e-8)
                self.assertAlmostEqual(result.saturation_out, reference[1], delta=3e-8)
                assert_vec_near(self, out_xyz, reference[2], tol=8e-8)

    def test_color_space_conversion_without_compression_is_colorimetric(self):
        xyz = (0.22, 0.31, 0.12)
        source_rgb = xyz_d65_to_encoded_rgb(xyz, DWG_INTERMEDIATE)
        result = apply_satcomp_encoded(
            source_rgb, DWG_INTERMEDIATE, ACESCCT,
            threshold=10.0, ratio=4.0, knee=0.1,
        )
        recovered_xyz = encoded_rgb_to_xyz_d65(result.rgb, ACESCCT)
        assert_vec_near(self, xyz, recovered_xyz, tol=8e-8)
        self.assertFalse(result.changed)

    def test_davinci_intermediate_official_mapping_values(self):
        mappings = [
            (-0.01, -0.104443),
            (0.0, 0.0),
            (0.18, 0.336043),
            (1.0, 0.513837),
            (10.0, 0.756599),
            (40.0, 0.903125),
            (100.0, 1.0),
        ]
        for linear, encoded in mappings:
            self.assertAlmostEqual(davinci_intermediate_encode_channel(linear), encoded, delta=6e-7)


if __name__ == "__main__":
    unittest.main()
