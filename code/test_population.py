import unittest
from dataclasses import replace
from population import Stratum, Implementation, evaluate, outcomes


class PopulationTests(unittest.TestCase):
    def test_full_delivery_legacy(self):
        for p in (0, .2, .6, 1):
            for r in (0, .5, 1):
                actual = evaluate([Stratum('all', 1, p=p, r=r)])['delta']
                for k, v in outcomes(p, r)['delta'].items():
                    self.assertAlmostEqual(actual[k], v)

    def test_unknown_no_trigger(self):
        x = evaluate([Stratum('unknown', 1, rose='unknown')])
        self.assertEqual(x['strata'][0]['patients'], 100)
        self.assertTrue(all(v == 0 for v in x['delta'].values()))

    def test_no_concern(self):
        self.assertEqual(evaluate([Stratum('a', 1, rose='no_concern')])['strata'][0]['completed'], 0)

    def test_wait_for_surgery(self):
        self.assertEqual(evaluate([Stratum('a', 1, current_need=False)])['strata'][0]['triggered'], 0)

    def test_no_suspicion(self):
        self.assertEqual(evaluate([Stratum('a', 1, suspected_malignancy=False)])['strata'][0]['triggered'], 0)

    def test_infeasible(self):
        x = evaluate([Stratum('a', 1, feasible=0)])
        self.assertEqual(x['strata'][0]['triggered'], 100)
        self.assertEqual(x['strata'][0]['no_attempt'], 100)
        self.assertEqual(x['delta']['cost'], 0)

    def test_no_attempt(self):
        self.assertEqual(evaluate([Stratum('a', 1, attempt=0)])['delta']['cost'], 0)

    def test_aborted(self):
        x = evaluate([Stratum('a', 1, completion=0)])
        self.assertAlmostEqual(x['delta']['cost'], 10300)
        self.assertAlmostEqual(x['delta']['expected_events'], .1)
        self.assertEqual(x['delta']['nsclc_ready'], 0)

    def test_non_target_cost_and_no_hindsight(self):
        x = evaluate([Stratum('a', 1, target_nsclc=False)])
        self.assertEqual(x['strata'][0]['triggered'], 100)
        self.assertAlmostEqual(x['delta']['cost'], 61500)
        self.assertAlmostEqual(x['delta']['expected_events'], .5)
        self.assertEqual(x['delta']['nsclc_ready'], 0)

    def test_zero_effect_charged(self):
        self.assertAlmostEqual(evaluate([Stratum('a', 1, r=0)])['delta']['cost'], 61500)

    def test_hand_formula(self):
        x = evaluate([Stratum('target', .4), Stratum('other', .1, target_nsclc=False),
                      Stratum('unknown', .5, rose='unknown')], Implementation(screening_cost=2, fixed_cost=100))
        expected = 40*(615-1946.8*.6*.8)+10*615+300
        self.assertAlmostEqual(x['delta']['cost'], expected)
        self.assertAlmostEqual(x['delta']['repeat_operations'], -40*.6*.8*.7*.5*.8)

    def test_mass_and_scaling(self):
        s = [Stratum('a', .4, feasible=.8, attempt=.7, completion=.9), Stratum('b', .6, rose='unknown')]
        x, y = evaluate(s), evaluate(s, n=200)
        for row in x['strata']:
            self.assertAlmostEqual(row['patients'], row['completed']+row['aborted']+row['no_attempt'])
        self.assertAlmostEqual(sum(z['patients'] for z in x['strata']), 100)
        for k in x['delta']:
            self.assertAlmostEqual(y['delta'][k], 2*x['delta'][k])

    def test_invalid_inputs(self):
        base = Stratum('a', 1)
        for kwargs in ({'p':float('nan')}, {'weight':-1}, {'feasible':1.2}, {'rose':'missing'}, {'current_need':1}):
            with self.assertRaises(ValueError): evaluate([replace(base, **kwargs)])
        with self.assertRaises(ValueError): evaluate([replace(base, weight=.5)])
        with self.assertRaises(ValueError): evaluate([base], Implementation(screening_cost=-1))


if __name__ == '__main__':
    unittest.main()
