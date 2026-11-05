"""Focused actual-DCTL regression; compiler availability is a prebuild requirement."""
import unittest
from tools.build_native import build
from tools.scalar_measure import regression


class NativeRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Never accept an executable left over from a different DCTL revision.
        build()

    def test_near_limiter_tail_rounding(self):
        result=regression()
        self.assertGreater(result['historical_absolute_error'],result['case_absolute_bound'])
        self.assertLessEqual(result['absolute_error'],result['case_absolute_bound'])


if __name__=='__main__':
    unittest.main()
