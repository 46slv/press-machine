"""Native safety regressions for CUDA-oriented compensation; GPU gate is explicit."""
import gzip
import json
import math
from pathlib import Path
import unittest
from reference import oracle as o
from tools import domain_probe as d
from tools.build_native import ROOT,build
from tools.generate_precision_candidate import generate_source
from tools.cuda_vectors import extra_pixels

EXE=ROOT/'build/precision_native.exe'

class CudaRoundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build('tests/precision_harness.cpp',EXE)

    def test_source_rounding_bindings_and_independent_constants(self):
        source=(ROOT/'dctl/PressMachine_R2.dctl').read_text()
        self.assertEqual(source,generate_source())
        for intrinsic in ('__fadd_rn','__fsub_rn','__fmul_rn','__fdiv_rn','__fmaf_rn'):
            self.assertIn(intrinsic,source)
        self.assertIn('(__float_as_int(t) & 0x7fffffff)==0',source)
        generator=(ROOT/'tools/precision_inverse_source.py').read_text()
        self.assertNotIn('from reference',generator)
        self.assertNotIn('import oracle',generator)

    def test_newton_roots_zero_and_finite_range(self):
        values=[0.,1e-24,1e-12,.001,1.,1e6,1e24,4e37,o.F32_MAX]
        values=[o.f32(v) for v in values]
        signed=values+[-v for v in values[1:]]
        rows=d.native([('R',(v,0.,0.),(25.,75.,20.,False)) for v in signed],EXE)
        for v,row in zip(signed,rows):
            self.assertTrue(all(map(math.isfinite,row)))
            expected=math.cbrt(v)
            self.assertLessEqual(abs(math.fsum(row[:2])-expected)/max(1.,abs(expected)),1e-11)
        self.assertEqual(rows[0][:2],(0.,0.))
        rows=d.native([('H',(v,0.,0.),(25.,75.,20.,False)) for v in values],EXE)
        for v,row in zip(values,rows):
            self.assertTrue(all(map(math.isfinite,row)))
            self.assertLessEqual(abs(math.fsum(row[:2])-math.sqrt(v))/max(1.,math.sqrt(v)),1e-11)

    def test_HDR_cancellation_adjacent_inputs(self):
        # First 771 vectors are fixed one-coordinate ULP neighbors of host's
        # difficult HDR output cancellation, not chosen using candidate output.
        rgbs=[tuple(map(float,rgb)) for rgb in extra_pixels()[:771]]
        rows=d.native([('P',rgb,(25.,75.,20.,False)) for rgb in rgbs],EXE)
        maximum=0.
        for rgb,actual in zip(rgbs,rows):
            expected=o.apply(rgb,25.,75.,20.).rgb
            maximum=max(maximum,max(abs(a-b) for a,b in zip(actual,expected))/max(1.,*map(abs,expected)))
        self.assertLessEqual(maximum,2**-13)
        self.assertLess(maximum,2e-6)

    def test_saved_host_expectations_are_independent_double(self):
        path=ROOT/'evidence/cuda-rounding-20261107/host-numeric-fixture.json.gz'
        with gzip.open(path,'rt') as file: fixture=json.load(file)
        records=fixture['records']
        self.assertEqual(len(records),9894)
        for i in (0,1,572,8195,8273,9075,9624,9891):
            record=records[i]
            expected=o.apply(tuple(map(float,record['rgba'][:3])),25.,75.,20.)
            self.assertEqual(list(expected.rgb),record['expected_c75']['rgb'])

if __name__=='__main__':unittest.main()
