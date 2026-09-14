"""Conditional NSCLC analysis; ALL inputs hypothetical. Standard library calculation."""
from pathlib import Path
from dataclasses import asdict
import json,csv,math
from integrated import Settings,State,run
ROOT=Path(__file__).resolve().parent
CFG=Settings(horizon=120)
FLAGS=((True,True),(True,False),(False,True),(False,False))
METRICS=('cost','repeat_operations','expected_events','nsclc_ready','nsclc_marker_complete')
BASIS=[run([State(1,'nsclc',s,m)],CFG) for s,m in FLAGS]
EXTRA={'cost':615,'expected_events':.005}

def weights(p,r,g=.3,relation='independent'):
    for x in (p,r,g):
        if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<=1:raise ValueError('probability')
    if relation not in ('lower','independent','upper'):raise ValueError('relation')
    j={'lower':max(0,p+g-1),'independent':p*g,'upper':min(p,g)}[relation]
    a=[1-p-g+j,p-j,g-j,j]
    b=[a[0]+r*a[1],(1-r)*a[1],a[2]+r*a[3],(1-r)*a[3]]
    return [max(0,x) for x in a],[max(0,x) for x in b]

def outcomes(p,r,relation='independent'):
    a,b=weights(p,r,relation=relation)
    A={k:100*sum(w*v[k] for w,v in zip(a,BASIS)) for k in METRICS}
    B={k:100*(sum(w*v[k] for w,v in zip(b,BASIS))+EXTRA.get(k,0)) for k in METRICS}
    return {'A':A,'B':B,'delta':{k:B[k]-A[k] for k in METRICS}}

def threshold(p,relation='independent'):
    y0=outcomes(p,0,relation)['delta']['cost'];y1=outcomes(p,1,relation)['delta']['cost']
    if y1>1e-9:return None
    return y0/(y0-y1)

def main():
    import unittest
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover(str(ROOT),pattern='test_*.py'))
    if not result.wasSuccessful():raise SystemExit(1)
    rows=[]
    for relation in ('independent','lower','upper'):
        for ip in range(101):
            for ir in range(101):
                p,r=ip/100,ir/100;o=outcomes(p,r,relation)
                rows.append(dict(relation=relation,p=p,r=r,**{f'{a}_{k}':v for a,metrics in o.items() for k,v in metrics.items()}))
    with (ROOT/'grid.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    report={'status':'ALL INPUTS HYPOTHETICAL; NOT CALIBRATED',
      'denominator':'100 trigger-eligible, technically/safety feasible patients with initial TBNA-confirmed target NSCLC; conditional analysis; 100% delivery',
      'bundle':'EGFR and ALK decision-specific scenario; not an assay adequacy estimate',
      'settings':asdict(CFG),'g':.3,'cryo_cost':600,'cryo_event':.005,'cryo_event_cost':3000,
      'thresholds':[{ 'relation':rel,'p':p,'r_threshold':threshold(p,rel)} for rel in ('independent','lower','upper') for p in (.2,.4,.6,.8,1)],
      'examples':[{ 'p':p,'r':r,**outcomes(p,r)} for p,r in ((.4,.5),(.6,.8),(.8,.8))]}
    (ROOT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'thresholds':report['thresholds'],'examples':report['examples']},indent=2))
if __name__=='__main__':main()
