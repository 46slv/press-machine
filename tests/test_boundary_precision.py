"""Precision repair regressions; an Oklab cusp is not a fixed visual defect."""
import json
import math
import random
import unittest
from reference import oracle as o
from tools import boundary_diagnosis as b
from tools import domain_probe as d
from tools.build_native import ROOT, build
from tools.generate_precision_candidate import generate_source

PRECISION_EXE=ROOT/'build'/'precision_native.exe'


class BoundaryPrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        build('tests/precision_harness.cpp',PRECISION_EXE)

    def test_source_reproducible_from_unchanged_reference_constants(self):
        self.assertEqual((ROOT/'dctl/PressMachine_R2.dctl').read_text(encoding='utf-8'),
                         generate_source())

    def test_recorded_cusp_matches_independent_oracle(self):
        result=b.recorded_pair()
        self.assertLess(result['max_encoded_native_oracle_error'],2**-13)
        self.assertGreater(abs(result['oracle_blue_delta']),.02)
        self.assertLess(abs(result['oracle_blue_delta']),.022)
        self.assertLess(abs(result['native_blue_delta']-result['oracle_blue_delta']),1e-5)

    def test_double_reference_cusp_is_continuous_not_jump(self):
        result=b.convergence()
        self.assertGreater(result['crossing_L'],.2)
        rows=result['rows']
        self.assertTrue(all(0<later['max_channel_delta']<earlier['max_channel_delta']
                            for earlier,later in zip(rows,rows[1:])))
        self.assertLess(rows[-1]['max_channel_delta'],rows[0]['max_channel_delta']/100)
        self.assertLess(abs(rows[-1]['ratio_to_previous_delta']-4**(-1/3)),1e-5)

    def test_focused_boundary_respects_unchanged_rgb_budget(self):
        result=b.focused_numeric()
        self.assertEqual(result['samples'],8196)
        self.assertEqual(result['outside_existing_empirical_envelope'],0)
        self.assertLessEqual(result['worst']['normalized_error'],2**-13)

    def test_original_L_guard_is_not_silently_revised(self):
        inputs=[tuple(map(o.f32,map(o.encode,b.linear_at(i/1023)))) for i in (689,690)]
        actual=d.native([('P',rgb,b.PARAMS) for rgb in inputs],d.EXE)
        self.assertEqual(tuple(map(o.bits,actual[1])),tuple(map(o.bits,inputs[1])))
        self.assertGreater(abs(o.decode(actual[1][2])-o.decode(actual[0][2])),.7)

    def test_compensated_DI_decode_pairs(self):
        rng=random.Random(120220261108)
        values=[o.f32(rng.uniform(-2.,8.5)) for _ in range(4000)]
        cut=o.bits(.02740668)
        values += [o.from_bits(cut+i) for i in range(-2,3)]
        for n in range(-6,110):
            code=o.f32((n+7)*.07329248)
            values += [o.from_bits(o.bits(code)+i) for i in (-1,0,1)]
        rows=d.native([('Q',(v,0.,0.),b.PARAMS) for v in values],PRECISION_EXE)
        maximum=0.
        for v,row in zip(values,rows):
            expected=o.decode(v)
            actual=math.fsum(row[:2])
            maximum=max(maximum,abs(actual-expected)/max(1.,abs(expected)))
        # Conservative pair-arithmetic allowance. This is decode verification,
        # not a widened pixel envelope.
        self.assertLessEqual(maximum,1024*2**-48)

    def test_all_LMS_cancellation_planes(self):
        result=b.cancellation_planes()
        self.assertTrue(all(n>0 for n in result['plane_counts']))
        self.assertEqual(result['outside_existing_empirical_envelope_or_nonfinite'],0)

    def test_precision_routing_seams(self):
        result=b.routing_seams()
        self.assertEqual(result['samples'],130)
        self.assertEqual(result['outside_existing_empirical_envelope'],0)

    def test_exponent127_fallback_transition(self):
        center=o.bits((127+7)*.07329248)
        values=[o.from_bits(center+i) for i in range(-4,5)]
        rows=d.native([('Q',(v,0.,0.),b.PARAMS) for v in values],PRECISION_EXE)
        self.assertTrue(all(all(map(math.isfinite,row)) for row in rows))
        for v,row in zip(values,rows):
            expected=o.decode(v)
            self.assertLess(abs(math.fsum(row[:2])-expected)/expected,2**-15)
        # Above 127, the existing standard decode owns the finite/range path.
        v=o.f32(9.85)
        precise=d.native([('Q',(v,0.,0.),b.PARAMS)],PRECISION_EXE)[0]
        ordinary=d.native([('E',(0.,v,0.),b.PARAMS)],PRECISION_EXE)[0]
        self.assertEqual(o.bits(precise[0]),o.bits(ordinary[1]))
        self.assertEqual(precise[1],0.)


if __name__=='__main__':
    unittest.main()
