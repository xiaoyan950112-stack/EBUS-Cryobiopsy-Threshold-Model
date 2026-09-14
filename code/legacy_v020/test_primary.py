import unittest
from reproduce import weights,outcomes,threshold,FLAGS,CFG,EXTRA,METRICS
from integrated import State,run
class PrimaryTests(unittest.TestCase):
    def test_full_tree_agreement(self):
        for rel in ('lower','independent','upper'):
            for p,r in ((0,0),(.4,.7),(1,1)):
                a,b=weights(p,r,relation=rel);o=outcomes(p,r,rel)
                for arm,ws in [('A',a),('B',b)]:
                    tree=run([State(w,'nsclc',s,m) for w,(s,m) in zip(ws,FLAGS)],CFG)
                    for k in METRICS:
                        self.assertAlmostEqual(o[arm][k],100*(tree[k]+(EXTRA.get(k,0) if arm=='B' else 0)),places=7)
    def test_zero_benefit_still_charged(self):
        d=outcomes(.6,0)['delta'];self.assertAlmostEqual(d['cost'],61500)
        self.assertAlmostEqual(d['expected_events'],.5)
        self.assertAlmostEqual(d['nsclc_ready'],0)
    def test_joint_mass_and_marginals(self):
        for rel in ('lower','independent','upper'):
            for p in (0,.3,.6,1):
                a,b=weights(p,.7,relation=rel)
                for w in (a,b):
                    self.assertAlmostEqual(sum(w),1);self.assertGreaterEqual(min(w),-1e-12)
                    self.assertAlmostEqual(w[2]+w[3],.3)
                self.assertAlmostEqual(b[1]+b[3],p*.3)
    def test_threshold_root(self):
        for rel in ('lower','independent','upper'):
            for p in (.2,.4,.6,.8,1):
                t=threshold(p,rel)
                if t is None:self.assertGreater(outcomes(p,1,rel)['delta']['cost'],0)
                else:self.assertAlmostEqual(outcomes(p,t,rel)['delta']['cost'],0,places=7)
    def test_extreme_no_failure_no_report_gain(self):
        d=outcomes(0,1)['delta'];self.assertAlmostEqual(d['nsclc_marker_complete'],0)
    def test_independent_path_formula(self):
        # Standalone formulas from alternative and repeat-operation branches.
        molecular_only_cost=250+.5*.8*(6000+.02*3000)
        for p,r in ((.4,.5),(.6,.8),(.8,1)):
            j=.3*p;d=outcomes(p,r)['delta']
            self.assertAlmostEqual(d['cost'],100*(615-r*((p-j)*molecular_only_cost+j*250)),places=7)
            self.assertAlmostEqual(d['repeat_operations'],-100*r*(p-j)*.4)
            self.assertAlmostEqual(d['expected_events'],.5-100*r*(p-j)*.4*.02)
            self.assertAlmostEqual(d['nsclc_ready'],100*r*((p-j)*.14+j*.08))
    def test_invalid_parameters(self):
        for p in (-.1,1.1,float('nan'),True):
            with self.assertRaises(ValueError):weights(p,.5)
if __name__=='__main__':unittest.main()
