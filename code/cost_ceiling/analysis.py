"""Cost ceilings per fully delivered conditional patient; illustrative dollars."""
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
import csv
import unittest

@dataclass(frozen=True)
class Rescue:
    alternative_success: float = .5
    uptake: float = .8
    alternative_cost: float = 250
    repeat_expected_cost: float = 6060  # 6000 + .02 * 3000, ALL hypothetical

def check_probability(x):
    if isinstance(x, bool) or not isfinite(x) or not 0 <= x <= 1:
        raise ValueError('Probability must be finite and between zero and one')

def basis(a):
    check_probability(a.alternative_success); check_probability(a.uptake)
    if any(not isfinite(x) or x < 0 for x in (a.alternative_cost,a.repeat_expected_cost)):
        raise ValueError('Costs must be finite and nonnegative')
    L,C,s,u=a.alternative_cost,a.repeat_expected_cost,a.alternative_success,a.uptake
    return (0, L+(1-s)*u*C, u*C, L+u*C)

def ceiling(p,r,g=.3,j=None,a=Rescue(),b=None):
    """Maximum total expected add-on cost. Negative means no nonnegative ceiling.
    State order: complete, molecular-only, staging-only, both incomplete.
    A/B residual molecular failures may have different rescue. B initially
    molecular-complete / stage-incomplete states retain A rescue as in legacy.
    All modeled operations are within horizon; no timing displacement.
    """
    for x in (p,r,g): check_probability(x)
    j=p*g if j is None else j
    if not isfinite(j) or not max(0,p+g-1)-1e-12 <= j <= min(p,g)+1e-12:
        raise ValueError('Infeasible joint probability')
    b=a if b is None else b
    A=basis(a); B=list(basis(b)); B[2]=A[2]
    w=(1-p-g+j,p-j,g-j,j)
    v=(w[0]+r*w[1],(1-r)*w[1],w[2]+r*w[3],(1-r)*w[3])
    return sum(x*y for x,y in zip(w,A))-sum(x*y for x,y in zip(v,B))

def probe_budget(total_ceiling, minute_cost, extra_pathology, expected_addon_harm=15,
                 extra_minutes=5.3, other_cost=0):
    """Residual probe/access budget; 5.3 min trial anchor, other defaults hypothetical."""
    vals=(minute_cost,extra_pathology,expected_addon_harm,extra_minutes,other_cost)
    if any(not isfinite(x) or x<0 for x in vals): raise ValueError('Invalid resources')
    return total_ceiling-extra_minutes*minute_cost-extra_pathology-expected_addon_harm-other_cost

class Checks(unittest.TestCase):
    def test_original_identity(self):
        self.assertAlmostEqual(ceiling(.6,.8),1946.8*.6*.8)
        self.assertAlmostEqual(100*(615-ceiling(.6,.8)),-31946.4)
    def test_equal_closed_form_grid(self):
        for p in (0,.2,.6,1):
            for r in (0,.5,1):
                for g in (0,.3,1):
                    for u in (0,.4,1):
                        a=Rescue(uptake=u)
                        self.assertAlmostEqual(ceiling(p,r,g,a=a),p*r*(250+(1-g)*.5*u*6060))
    def test_no_effect(self): self.assertAlmostEqual(ceiling(.6,0),0)
    def test_staging_all(self): self.assertAlmostEqual(ceiling(.6,.8,1),.6*.8*250)
    def test_no_repeat(self): self.assertAlmostEqual(ceiling(.6,.8,a=Rescue(uptake=0)),120)
    def test_differential_no_effect_is_not_sampling(self):
        self.assertLess(ceiling(.6,0,b=Rescue(.2,1)),0)
    def test_fan_is_separate(self):
        self.assertAlmostEqual(ceiling(8/38,7/8),1946.8*7/38)
    def test_budget(self): self.assertAlmostEqual(probe_budget(500,10,50),382)
    def test_invalid(self):
        for args in ((-.1,.8),(.6,1.1),(.6,.8,.3,.5)):
            with self.assertRaises(ValueError): ceiling(*args)

def generate():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=Path(__file__).parent
    rows=[]
    for tag,p,r in [('report_hypothetical',.6,.8),('suitability_full_bridge',8/38,7/8)]:
        for k in range(101):
            u=k/100
            for g in (0,.3,.6,1):
                for scenario in ('equal','differential'):
                    a=Rescue(uptake=u)
                    b=a if scenario=='equal' else Rescue(.2,min(1,u+.2))
                    rows.append(dict(endpoint=tag,p=p,r=r,g=g,u_A=u,u_B=b.uptake,
                                     scenario=scenario,total_expected_cost_ceiling=ceiling(p,r,g,a=a,b=b)))
    with (out/'ceiling_grid.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    fig,axes=plt.subplots(1,2,figsize=(12,5.6),sharey=True)
    colors=['#007C91','#3757A6','#BD7720']
    for ax,(tag,p,r,title) in zip(axes,[('report_hypothetical',.6,.8,'A. Required-report scenario\nEntirely hypothetical: p=0.60, r=0.80'),('suitability_full_bridge',8/38,7/8,'B. Suitability-based illustration\nFull translation to report benefit ASSUMED')]):
        xs=[i/100 for i in range(101)]
        for g,c in zip((0,.3,.6),colors):
            ax.plot(xs,[ceiling(p,r,g,a=Rescue(uptake=u)) for u in xs],color=c,lw=2,label=f'Staging incomplete: {g:.0%}')
        ax.plot(xs,[ceiling(p,r,.3,a=Rescue(uptake=u),b=Rescue(.2,min(1,u+.2))) for u in xs],color='#AA3B55',ls='--',lw=2,label='Different rescue; staging 30%')
        ax.axhline(0,color='#666666',lw=.8)
        ax.set_title(title,fontsize=11,loc='left');ax.set_xlim(0,1)
        ax.set_xlabel('A: repeat uptake AFTER alternative failure',fontsize=10)
        ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Maximum total expected add-on cost\nIllustrative dollars per delivered patient')
    axes[0].legend(fontsize=8,loc='upper left')
    fig.suptitle('Conditional cost-neutrality ceilings: not clinical adoption thresholds',fontsize=14)
    fig.text(.08,.025,'All costs hypothetical. No price year. Negative values: even a free add-on does not offset modeled rescue differences.\nPanel B is an explicit unvalidated bridge, not an observed report-completion effect. All rescue occurs within horizon.',fontsize=9)
    fig.tight_layout(rect=(0,.12,1,.93))
    # Deterministic export from the same figure; no image resampling or retouching.
    matplotlib.rcParams['pdf.fonttype'] = 42
    fig.savefig(out/'cost_ceiling.png', dpi=600)
    fig.savefig(out/'cost_ceiling.pdf')
    plt.close(fig)
    # Translation sensitivity: alpha is a modeling bridge, not a clinical estimate.
    bridge=[]
    for alpha in (0,.25,.5,.75,1):
        for u in (0,.25,.5,.75,1):
            bridge.append(dict(alpha=alpha,u=u,ceiling=ceiling(8/38,7/8*alpha,a=Rescue(uptake=u))))
    with (out/'translation_sensitivity.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=bridge[0]);w.writeheader();w.writerows(bridge)
    table=[]
    for u in (0,.25,.5,.75,.8,1):
        a=Rescue(uptake=u)
        table.append((u,ceiling(.6,.8,a=a),ceiling(8/38,7/8,a=a),ceiling(.6,.8,a=a,b=Rescue(.2,min(1,u+.2)))))
    print('u, report ceiling, full-bridge ceiling, differential report ceiling')
    for row in table: print(', '.join(f'{x:.4f}' for x in row))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful(): raise SystemExit(1)
    generate()
