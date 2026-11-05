import itertools
import math
from pathlib import Path
import re
import unittest
from reference import oracle as o

class ScalarTests(unittest.TestCase):
    def test_analytic_anchors(self):
        # T25 / width10 / 75% compression: knee midpoint reduction=.9375.
        for s,expected in ((0.,0.),(20.,20.),(25.,24.0625),(30.,26.25),(100.,43.75)):
            self.assertEqual(o.transfer(s,25.,75.,20.),expected)
        for p in (0.,20.,100.):
            self.assertEqual(o.transfer(300.,25.,100.,p),25.)
            self.assertEqual(o.transfer(300.,0.,75.,p),75.)

    def test_monotone_no_boost(self):
        for t,c,p in itertools.product((0.,25.,100.),(0.,25.,50.,75.,100.),(0.,20.,100.)):
            ss=[i/8 for i in range(4001)]
            ys=[o.transfer(s,t,c,p) for s in ss]
            self.assertTrue(all(0<=y<=s for s,y in zip(ss,ys)))
            self.assertTrue(all(a<=b for a,b in zip(ys,ys[1:])))
            for s,y in zip(ss,ys):
                if c==0 or s<=t*(1-p/100): self.assertEqual(s,y)

    def test_c1_and_high_slope(self):
        # Polynomial endpoint value/derivatives checked analytically, avoiding
        # a guessed finite-difference tolerance. Slope errors bounded by double u.
        for t,c,p in itertools.product((25.,100.),(25.,50.,75.,100.),(20.,100.)):
            a=c/100; k=2*t*p/100; lo=t*(1-p/100); hi=t*(1+p/100)
            self.assertEqual(lo-a*(lo-lo)**2/(2*k),lo)
            self.assertAlmostEqual(hi-a*(hi-lo)**2/(2*k),o.transfer(hi,t,c,p),places=12)
            self.assertEqual(1-a*(lo-lo)/k,1)
            self.assertAlmostEqual(1-a*(hi-lo)/k,1-a,places=14)
            self.assertEqual(o.transfer(hi+100,t,c,p)-o.transfer(hi,t,c,p),100*(1-a))

class ColorTests(unittest.TestCase):
    def test_official_di_anchors(self):
        # Official table is printed to 6 decimals. At 40 the published formula
        # yields .903124492603 (table .903125), just beyond nearest rounding.
        # One last printed decimal unit accommodates the source table itself.
        for x,v in ((-.01,-.104443),(0.,0.),(.18,.336043),(1.,.513837),
                    (10.,.756599),(40.,.903125),(100.,1.)):
            self.assertLessEqual(abs(o.encode(x)-v),1e-6)
            self.assertLessEqual(abs(o.decode(o.encode(x))-x),abs(x)*4e-15+1e-17)
        self.assertEqual(o.encode(.00262409),.00262409*10.44426855)
        self.assertEqual(o.decode(.02740668),.02740668/10.44426855)

    def test_dwg_primary_matrix(self):
        # Derive matrix independently from official xy chromaticities.
        def xy(x,y): return (x/y,1.,(1-x-y)/y)
        primaries=[xy(.8,.313),xy(.1682,.9877),xy(.079,-.1155)]
        # Solve primary scaling by Cramer's rule, not the production matrix.
        def det(m):
            return sum(m[0][j]*(m[1][(j+1)%3]*m[2][(j+2)%3]-m[1][(j+2)%3]*m[2][(j+1)%3]) for j in range(3))
        m=tuple(zip(*primaries)); white=xy(.3127,.329)
        scales=[]
        for j in range(3):
            replaced=tuple(tuple(white[r] if c==j else m[r][c] for c in range(3)) for r in range(3))
            scales.append(det(replaced)/det(m))
        for r,c in itertools.product(range(3),repeat=2):
            self.assertLessEqual(abs(m[r][c]*scales[c]-o.DWG_XYZ[r][c]),.5e-8)

    def test_oklab_roundtrip_and_negative_roots(self):
        for xyz in ((.950455927,1.,1.08905775),(.4,.2,-.1),(-.1,.2,.4),(-1.,-.1,-.5),(5.,10.,2.)):
            out=o.lab_xyz(o.xyz_lab(xyz))
            self.assertTrue(all(math.isfinite(x) for x in out))
            self.assertLess(max(abs(a-b) for a,b in zip(xyz,out)),64*math.ulp(max(map(abs,xyz))))
        self.assertLess(min(o.mul(o.XYZ_LMS,(-.1,.2,.4))),0)

    def test_exposure_invariance(self):
        for rgb in ((.8,.08,.01),(.01,.1,.9),(-.2,.3,.8)):
            s=o.saturation(o.linear_lab(rgb))
            for scale in (2**-12,.5,2.,2**12):
                self.assertLess(abs(o.saturation(o.linear_lab(tuple(x*scale for x in rgb)))-s),64*math.ulp(s))

    def test_chroma_only(self):
        # Printed 8-decimal DWG inverse has a measured matrix-product residual.
        # Allow its propagation plus 64 double ULPs, rather than exact inversion.
        for rgb in ((.8,.08,.01),(.2,.3,.9),(-.04,.3,1.2),(1000.,2.,.1)):
            encoded=tuple(o.encode(x) for x in rgb)
            before=o.encoded_lab(encoded)
            out=o.apply(encoded,25.,75.,20.)
            self.assertEqual(out.path,'compressed')
            after=o.encoded_lab(out.rgb)
            target=(before[0],*(x*out.s_out/out.s_in for x in before[1:]))
            xyz=o.lab_xyz(target)
            returned=o.mul(o.DWG_XYZ,o.mul(o.XYZ_DWG,xyz))
            error=max(abs(a-b) for a,b in zip(xyz,returned))+64*math.ulp(max(map(abs,xyz)))
            lms=o.mul(o.XYZ_LMS,xyz)
            lms_error=max(sum(map(abs,row)) for row in o.XYZ_LMS)*error
            # Mean-value bound on signed cbrt away from zero for these samples.
            min_lms=min(map(abs,lms))-lms_error
            self.assertGreater(min_lms,0)
            bound=max(sum(map(abs,row)) for row in o.ROOT_LAB)*lms_error/(3*min_lms**(2/3))
            self.assertLess(max(abs(a-b) for a,b in zip(after,target)),bound+64*math.ulp(max(map(abs,target))))

    def test_exact_identity_and_extended_range(self):
        for rgb in ((-.2,.5,1.3),(-0.,0.,1.),(.336043,)*3,(1e-20,2e-20,3e-20)):
            for params in ((25.,0.,20.,False),(25.,75.,20.,True)):
                self.assertEqual(tuple(map(o.bits,o.apply(rgb,*params).rgb)),tuple(map(o.bits,rgb)))
        rgb=(-.2,.5,1.3)
        self.assertEqual(o.apply(rgb,200.,75.,20.).rgb,rgb)
        out=o.apply(tuple(o.encode(x) for x in (-.2,.05,.5)),0.,25.,0.)
        self.assertLess(min(out.rgb),0)
        out=o.apply(tuple(o.encode(x) for x in (1000.,2.,.1)),25.,50.,20.)
        self.assertGreater(max(out.rgb),1)

    def test_domain_and_nonfinite(self):
        # This finite DWG blue has negative Oklab L; it must take the specified
        # invalid-domain identity rather than receive an artistic repair.
        blue=tuple(o.encode(x) for x in (.01,.01,.9))
        self.assertEqual(o.apply(blue,25.,75.,20.).path,'domain_identity')
        for l,c in ((1e-6,.2),(.5,1e-7),(-.5,.2)):
            self.assertFalse(o.valid_domain((l,c,0),c,100*c/l))
        self.assertFalse(o.valid_domain((1,.2,0),.2,1e-7))
        self.assertTrue(o.valid_domain((1.001e-6,1.001e-7,0),1.001e-7,10.))
        for rgb in ((o.F32_MAX,0.,.5),(-o.F32_MAX,-o.F32_MAX/2,0.)):
            out=o.apply(rgb,25.,75.,20.)
            self.assertTrue(all(math.isfinite(x) for x in out.rgb))
            self.assertEqual(out.rgb,rgb)

class SourceTests(unittest.TestCase):
    def test_four_controls_and_rgb_entry(self):
        src=(Path(__file__).resolve().parents[1]/'dctl/PressMachine_R2.dctl').read_text()
        self.assertEqual(len(re.findall(r'^DEFINE_UI_PARAMS\(',src,re.M)),4)
        self.assertRegex(src,r'__DEVICE__ float3 transform\(')
        self.assertNotRegex(src,r'_clamp|_saturate|Density|skin|LumaMix|INPUT_COLOR_SPACE')

if __name__ == '__main__': unittest.main()
