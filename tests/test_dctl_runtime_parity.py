import ctypes
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from color_model import (
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
    xyz_d65_to_encoded_rgb,
)


class Float3(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float)]


ENCODING_ENUMS = {
    LINEAR_REC709.name: (0, 0),
    SRGB.name: (0, 1),
    REC709_OETF.name: (0, 2),
    REC709_GAMMA24.name: (0, 3),
    LINEAR_REC2020.name: (1, 0),
    LINEAR_DWG.name: (2, 0),
    DWG_INTERMEDIATE.name: (2, 4),
    LINEAR_ACESCG.name: (3, 0),
    ACESCCT.name: (3, 5),
}

ENCODINGS = (
    LINEAR_REC709,
    SRGB,
    REC709_OETF,
    REC709_GAMMA24,
    LINEAR_REC2020,
    LINEAR_DWG,
    DWG_INTERMEDIATE,
    LINEAR_ACESCG,
    ACESCCT,
)


class DctlRuntimeParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clang = shutil.which("clang")
        if not clang:
            raise unittest.SkipTest("clang is required for the DCTL native parity harness")
        cls._tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(__file__).resolve().parents[1]
        lib = pathlib.Path(cls._tmp.name) / "libsatcomp_dctl.so"
        subprocess.run(
            [
                clang,
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O0",
                "-I", str(root / "tests"),
                "-I", str(root),
                str(root / "tests" / "dctl_runtime_harness.c"),
                "-lm",
                "-o", str(lib),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.satcomp_run.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int,
        ]
        cls.lib.satcomp_run.restype = Float3

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "_tmp"):
            cls._tmp.cleanup()

    def run_dctl(self, rgb, input_encoding, output_encoding=None, threshold=0.25, ratio=3.0, knee=0.10):
        if output_encoding is None:
            output_encoding = input_encoding
        in_gamut, in_transfer = ENCODING_ENUMS[input_encoding.name]
        out_gamut, out_transfer = ENCODING_ENUMS[output_encoding.name]
        same = output_encoding == input_encoding
        out = self.lib.satcomp_run(
            rgb[0], rgb[1], rgb[2],
            in_gamut, in_transfer,
            0 if same else out_gamut + 1,
            0 if same else out_transfer + 1,
            threshold, ratio, knee,
            0,
        )
        return (out.x, out.y, out.z)

    def test_dctl_matches_cpu_oracle_across_supported_encodings(self):
        xyz_samples = (
            (0.18 * 0.9504559271, 0.18, 0.18 * 1.0890577508),
            (0.31, 0.22, 0.08),
            (0.22, 0.31, 0.12),
            (0.10, 0.06, 0.35),
            (0.85, 0.32, 0.06),
        )
        for encoding in ENCODINGS:
            for xyz in xyz_samples:
                with self.subTest(encoding=encoding.name, xyz=xyz):
                    rgb = xyz_d65_to_encoded_rgb(xyz, encoding)
                    expected = apply_satcomp_encoded(
                        rgb,
                        encoding,
                        encoding,
                        threshold=0.25,
                        ratio=3.0,
                        knee=0.10,
                    ).rgb
                    actual = self.run_dctl(rgb, encoding)
                    for channel, (got, want) in enumerate(zip(actual, expected)):
                        self.assertAlmostEqual(
                            got, want, delta=6e-5,
                            msg=f"channel={channel} got={got} want={want}",
                        )


    def test_dctl_matches_cpu_oracle_across_standard_input_output_pairs(self):
        xyz_samples = (
            (0.31, 0.22, 0.08),
            (0.10, 0.06, 0.35),
            (0.85, 0.32, 0.06),
        )
        for input_encoding in ENCODINGS:
            for output_encoding in ENCODINGS:
                for xyz in xyz_samples:
                    with self.subTest(input=input_encoding.name, output=output_encoding.name, xyz=xyz):
                        rgb = xyz_d65_to_encoded_rgb(xyz, input_encoding)
                        expected = apply_satcomp_encoded(
                            rgb,
                            input_encoding,
                            output_encoding,
                            threshold=0.25,
                            ratio=3.0,
                            knee=0.10,
                        ).rgb
                        actual = self.run_dctl(rgb, input_encoding, output_encoding)
                        for channel, (got, want) in enumerate(zip(actual, expected)):
                            self.assertAlmostEqual(
                                got, want, delta=8e-5,
                                msg=f"channel={channel} got={got} want={want}",
                            )

    def test_exact_identity_fast_path_is_bit_preserving(self):
        rgb = (1.234567, -0.125, 0.33333334)
        out = self.lib.satcomp_run(
            rgb[0], rgb[1], rgb[2],
            2, 4, 0, 0,
            0.25, 1.0, 0.10,
            0,
        )
        expected = tuple(ctypes.c_float(x).value for x in rgb)
        self.assertEqual((out.x, out.y, out.z), expected)


if __name__ == "__main__":
    unittest.main()
