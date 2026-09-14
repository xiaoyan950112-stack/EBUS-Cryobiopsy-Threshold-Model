"""Run from any directory: python3 run_population.py. Standard library only."""
from pathlib import Path
from dataclasses import asdict
import json
import unittest
from population import Stratum, Implementation, evaluate

ROOT = Path(__file__).resolve().parent

def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern='test_population.py')
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
    strata = [Stratum('target_concern_current', .3, feasible=.8, completion=.9),
              Stratum('non_target_concern_current', .1, target_nsclc=False, feasible=.8, completion=.9),
              Stratum('unknown', .2, rose='unknown'),
              Stratum('no_concern', .2, rose='no_concern'),
              Stratum('can_wait', .2, current_need=False)]
    cfg = Implementation(screening_cost=2)
    result = dict(inputs=[asdict(s) for s in strata], config=asdict(cfg), results=evaluate(strata, cfg))
    (ROOT/'results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['results'], indent=2))

if __name__ == '__main__': main()
