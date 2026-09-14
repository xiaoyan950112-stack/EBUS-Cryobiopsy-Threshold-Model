import unittest
from differential import Rescue, compare, threshold, SCENARIOS
from population import evaluate, Stratum, outcomes

class DifferentialTests(unittest.TestCase):
    def test_legacy_grid(self):
        for p in (0,.2,.6,1):
            for r in (0,.5,1):
                for k,v in outcomes(p,r)['delta'].items():
                    self.assertAlmostEqual(compare(p,r)['delta'][k], v)

    def test_hand_cost(self):
        p,r,s,u=.6,.4,.2,1
        # g=.3, j=.18. Residual molecular-only and joint masses.
        a_cost=p*250+(.3+(p-.18)*.5)*.8*6060
        b_cost=p*(1-r)*250+(.3-p*.3*(1-r))*.8*6060
        b_cost+=p*.3*(1-r)*u*6060+(p-.18)*(1-r)*(1-s)*u*6060+615
        self.assertAlmostEqual(compare(p,r,b=Rescue(alternative_success=s,repeat_uptake=u))['delta']['cost'],100*(b_cost-a_cost))

    def test_no_failures_no_differential(self):
        for b in SCENARIOS.values():
            self.assertAlmostEqual(compare(0,.5,b=b)['delta']['cost'],61500)

    def test_complete_rescue_no_residual_difference(self):
        for b in SCENARIOS.values():
            self.assertEqual(compare(.6,1,b=b)['B'],compare(.6,1)['B'])

    def test_lower_success_cost_equal_information_lower(self):
        x=compare(.6,.8); y=compare(.6,.8,b=SCENARIOS['lower_invasive_success'])
        self.assertAlmostEqual(x['delta']['cost'],y['delta']['cost'])
        self.assertLess(y['delta']['nsclc_ready'],x['delta']['nsclc_ready'])

    def test_roots(self):
        for b in SCENARIOS.values():
            t=threshold(.6,b=b)
            if t is not None and t>0:
                self.assertAlmostEqual(compare(.6,t,b=b)['delta']['cost'],0,places=7)

    def test_zero_effect_can_have_rescue_effect(self):
        self.assertNotEqual(compare(.6,0,b=SCENARIOS['combined'])['delta']['cost'],61500)

    def test_population_callback(self):
        b=SCENARIOS['combined']
        actual=evaluate([Stratum('a',1)],outcome_fn=lambda p,r:compare(p,r,b=b))['delta']
        for k,v in compare(.6,.8,b=b)['delta'].items():
            self.assertAlmostEqual(actual[k],v)

    def test_horizon_pending(self):
        b=SCENARIOS['longer_wait']
        x=compare(.6,.8,b=b,horizon=120);y=compare(.6,.8,b=b,horizon=240)
        self.assertGreater(y['B']['cost'],x['B']['cost'])
        self.assertGreater(y['B']['nsclc_ready'],x['B']['nsclc_ready'])

    def test_invalid(self):
        for b in (Rescue(alternative_success=-1),Rescue(joint=(1,1,0,0)),Rescue(repeat_wait=float('nan'))):
            with self.assertRaises(ValueError): compare(.6,.8,b=b)

if __name__=='__main__': unittest.main()
