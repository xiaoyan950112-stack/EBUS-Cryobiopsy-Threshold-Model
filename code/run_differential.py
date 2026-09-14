from pathlib import Path
from dataclasses import asdict
import json, unittest
from differential import compare, threshold, SCENARIOS, Rescue
from population import evaluate, Stratum, Implementation

ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    tests=unittest.defaultTestLoader.discover(str(ROOT),pattern='test_*.py')
    if not unittest.TextTestRunner(verbosity=1).run(tests).wasSuccessful(): raise SystemExit(1)
    strata=[Stratum('target',.3,feasible=.8,completion=.9),
            Stratum('non_target',.1,target_nsclc=False,feasible=.8,completion=.9),
            Stratum('unknown',.2,rose='unknown'),Stratum('no_concern',.2,rose='no_concern'),
            Stratum('can_wait',.2,current_need=False)]
    rows=[]
    for name,b in SCENARIOS.items():
        rows.append(dict(scenario=name,A_rescue=asdict(Rescue()),B_rescue=asdict(b),
            conditional=compare(.6,.8,b=b),r_threshold_at_p06=threshold(.6,b=b),
            population=evaluate(strata,Implementation(screening_cost=2),outcome_fn=lambda p,r:compare(p,r,b=b)),
            extended_horizon=compare(.6,.8,b=b,horizon=240)))
    result=dict(status='ALL INPUTS HYPOTHETICAL; NOT CLINICAL ESTIMATES',p=.6,r=.8,horizon=120,
                strata=[asdict(s) for s in strata],scenarios=rows)
    (ROOT/'differential_results.json').write_text(json.dumps(result,indent=2)+'\n')
    for row in rows:
        print(row['scenario'],row['r_threshold_at_p06'],row['conditional']['delta'],row['population']['delta']['cost'])
