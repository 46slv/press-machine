"""R2 scalar regression and a clearly isolated experimental domain proposal."""
import math
import unittest
from reference import oracle as o
from reference import continuous_oracle as co
from tools import domain_probe as d
from tools import scalar_measure as sm


class StabilityAndProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d.build_both()

    def test_original_frozen_budget_unchanged(self):
        sm.original_corpus({})

    def test_historical_adjacent_float_decrease(self):
        t,c,p=map(o.f32,(79.8,84.6,46.2))
        ss=tuple(map(o.f32,(116.66757202148438,116.6675796508789)))
        rows=d.native([('S',(s,0.,0.),(t,c,p,False)) for s in ss],d.EXE)
        self.assertLessEqual(rows[0][0],rows[1][0])
        for s,row in zip(ss,rows):
            self.assertLessEqual(abs(row[0]-o.transfer(s,t,c,p))/max(1.,abs(o.transfer(s,t,c,p))),2**-23)

    def test_expanded_scalar_monotonicity_and_frozen_accuracy(self):
        result=sm.measure(sm.expanded_cases(sm.expanded_states()))
        self.assertEqual(result['samples'],421486)
        for key in ('nonfinite','boosts','negatives','compression_zero_identity_failures','local_decreases'):
            self.assertEqual(result[key],0,key)
        self.assertLessEqual(result['max_normalized_error'],2**-23)

    def test_extended_high_tail_frozen_accuracy(self):
        result=sm.measure(sm.tail_cases())
        self.assertEqual(result['samples'],256256)
        for key in ('nonfinite','boosts','negatives','compression_zero_identity_failures','local_decreases'):
            self.assertEqual(result[key],0,key)
        self.assertLessEqual(result['max_normalized_error'],2**-23)

    def test_proposal_finite_no_boost_direct_scale(self):
        result=d.direct_report()
        self.assertEqual(result['nonfinite_negative_or_boost'],0)
        self.assertLessEqual(result['scale_max_absolute_error'],2**-23)

    def test_proposal_symmetric_continuous_zero_L_limit(self):
        cases=[('Q',(l,.8,0.),(25.,comp,20.,False))
               for comp in (50.,75.,100.) for l in (-1e-6,0.,1e-6)]
        rows=d.native(cases)
        for i,comp in enumerate((50.,75.,100.)):
            negative,zero,positive=(row[0] for row in rows[3*i:3*i+3])
            self.assertEqual(negative,positive)
            self.assertEqual(zero,1-comp/100)
            self.assertLessEqual(abs(positive-zero),1e-6)

    def test_blue_host_pair_is_guard_conflict_not_scalar(self):
        enc=[]
        for x in (689,690):
            u=x/1023
            enc.append(tuple(map(o.f32,map(o.encode,(.18*(1-u),.18*(1-u),.18*(1-u)+u)))))
        self.assertGreater(o.encoded_lab(enc[0])[0],1e-6)
        self.assertLess(o.encoded_lab(enc[1])[0],0)
        requests=[('P',rgb,(25.,75.,20.,False)) for rgb in enc]
        old=d.native(requests,d.EXE);new=d.native(requests)
        old_delta=abs(o.decode(old[1][2])-o.decode(old[0][2]))
        new_delta=abs(o.decode(new[1][2])-o.decode(new[0][2]))
        self.assertGreater(old_delta,.7)
        self.assertLess(new_delta,.001)
        self.assertEqual(o.apply(enc[1],25.,75.,20.).path,'domain_identity')
        self.assertEqual(co.apply(enc[1],25.,75.,20.).path,'compressed')

    def test_proposal_control_identity_exact(self):
        rgbs=[(-.2,.5,1.3),(-0.,0.,1.),tuple(map(o.f32,map(o.encode,(.01,.01,.9))))]
        for params in ((25.,0.,20.,False),(25.,75.,20.,True)):
            for rgb,row in zip(rgbs,d.native([('P',rgb,params) for rgb in rgbs])):
                self.assertEqual(tuple(map(o.bits,rgb)),tuple(map(o.bits,row)))


if __name__=='__main__':unittest.main()
