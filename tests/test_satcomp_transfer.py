import math
import unittest

from satcomp_transfer import compress_saturation


class SatCompTransferTests(unittest.TestCase):
    def test_ratio_one_is_exact_identity(self):
        for s in (0.0, 0.1, 0.65, 1.0, 2.5, 16.0):
            self.assertEqual(
                compress_saturation(s, threshold=0.65, ratio=1.0, knee=0.2),
                s,
            )

    def test_hard_knee_below_threshold_is_identity(self):
        for s in (0.0, 0.1, 0.649999):
            self.assertEqual(
                compress_saturation(s, threshold=0.65, ratio=4.0, knee=0.0),
                s,
            )

    def test_hard_knee_above_threshold_uses_ratio(self):
        self.assertAlmostEqual(
            compress_saturation(0.95, threshold=0.65, ratio=3.0, knee=0.0),
            0.75,
            places=12,
        )

    def test_soft_knee_matches_identity_at_lower_edge(self):
        t, r, k = 0.65, 3.0, 0.2
        lower = t - k / 2
        self.assertAlmostEqual(
            compress_saturation(lower, threshold=t, ratio=r, knee=k), lower, places=12
        )

    def test_soft_knee_matches_ratio_curve_at_upper_edge(self):
        t, r, k = 0.65, 3.0, 0.2
        upper = t + k / 2
        expected = t + (upper - t) / r
        self.assertAlmostEqual(
            compress_saturation(upper, threshold=t, ratio=r, knee=k), expected, places=12
        )

    def test_soft_knee_first_derivative_is_continuous(self):
        t, r, k = 0.65, 3.0, 0.2
        eps = 1e-6
        for edge, expected_slope in ((t - k / 2, 1.0), (t + k / 2, 1.0 / r)):
            y0 = compress_saturation(edge - eps, threshold=t, ratio=r, knee=k)
            y1 = compress_saturation(edge + eps, threshold=t, ratio=r, knee=k)
            slope = (y1 - y0) / (2 * eps)
            self.assertAlmostEqual(slope, expected_slope, places=5)

    def test_curve_is_monotonic_and_never_boosts_for_ratio_ge_one(self):
        params = dict(threshold=0.65, ratio=2.5, knee=0.15)
        xs = [i / 1000 for i in range(0, 3001)]
        ys = [compress_saturation(x, **params) for x in xs]
        self.assertTrue(all(a <= b for a, b in zip(ys, ys[1:])))
        self.assertTrue(all(y <= x + 1e-15 for x, y in zip(xs, ys)))

    def test_high_region_has_requested_slope(self):
        t, r, k = 0.65, 4.0, 0.2
        a, b = 1.2, 1.6
        ya = compress_saturation(a, threshold=t, ratio=r, knee=k)
        yb = compress_saturation(b, threshold=t, ratio=r, knee=k)
        self.assertAlmostEqual((yb - ya) / (b - a), 1.0 / r, places=12)

    def test_no_implicit_ceiling(self):
        y = compress_saturation(10.0, threshold=0.65, ratio=4.0, knee=0.2)
        self.assertGreater(y, 1.0)

    def test_invalid_parameters_fail(self):
        invalid_calls = [
            dict(saturation=-0.1, threshold=0.65, ratio=2.0, knee=0.1),
            dict(saturation=0.5, threshold=-0.1, ratio=2.0, knee=0.1),
            dict(saturation=0.5, threshold=0.65, ratio=0.5, knee=0.1),
            dict(saturation=0.5, threshold=0.65, ratio=2.0, knee=-0.1),
            dict(saturation=math.inf, threshold=0.65, ratio=2.0, knee=0.1),
        ]
        for kwargs in invalid_calls:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                compress_saturation(**kwargs)


if __name__ == "__main__":
    unittest.main()
