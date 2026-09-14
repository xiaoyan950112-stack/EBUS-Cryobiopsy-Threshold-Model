"""Arm-specific rescue among initially molecular-insufficient states only."""
from dataclasses import dataclass, replace
from functools import lru_cache
from population import number
from reproduce import CFG, FLAGS, METRICS, EXTRA, weights
from integrated import State, run

@dataclass(frozen=True)
class Rescue:
    alternative_success: float = .5
    repeat_uptake: float = .8
    repeat_success: float = .9
    joint: tuple = (.65, .15, .10, .10)
    alternative_days: float = 7
    repeat_wait: float = 14

    def validate(self):
        for k in ('alternative_success', 'repeat_uptake', 'repeat_success'):
            number(getattr(self, k), k, 1)
        for k in ('alternative_days', 'repeat_wait'):
            number(getattr(self, k), k)
        if len(self.joint) != 4 or abs(sum(self.joint)-1) > 1e-10:
            raise ValueError('joint mass')
        for v in self.joint: number(v, 'joint', 1)


@lru_cache(maxsize=128)
def basis(rescue, horizon):
    rescue.validate()
    cfg = replace(CFG, horizon=horizon)
    altered = replace(cfg, **vars(rescue))
    # Changes follow initial molecular failure, including its later stage-only rescue.
    # Initially molecular-complete/staging-incomplete cases retain shared settings.
    return [run([State(1, 'nsclc', s, m)], cfg if m else altered) for s, m in FLAGS]


def compare(p, r, a=Rescue(), b=Rescue(), horizon=120):
    a.validate(); b.validate()
    number(horizon, 'horizon')
    if horizon <= 0: raise ValueError('horizon')
    wa, wb = weights(p, r)
    A = {k:100*sum(w*v[k] for w,v in zip(wa,basis(a,horizon))) for k in METRICS}
    B = {k:100*(sum(w*v[k] for w,v in zip(wb,basis(b,horizon)))+EXTRA.get(k,0)) for k in METRICS}
    return {'A':A, 'B':B, 'delta':{k:B[k]-A[k] for k in METRICS}}


def threshold(p, a=Rescue(), b=Rescue(), horizon=120):
    y0=compare(p,0,a,b,horizon)['delta']['cost']
    y1=compare(p,1,a,b,horizon)['delta']['cost']
    if y0 <= 0: return 0.0
    if y1 > 0: return None
    return y0/(y0-y1)


SCENARIOS = {
    'equal': Rescue(),
    'lower_alternative': Rescue(alternative_success=.2),
    'more_invasive': Rescue(repeat_uptake=1),
    'lower_invasive_success': Rescue(repeat_success=.6, joint=(.40,.25,.10,.25)),
    'combined': Rescue(alternative_success=.2, repeat_uptake=1,
                       repeat_success=.6, joint=(.40,.25,.10,.25)),
    'longer_wait': Rescue(alternative_days=30, repeat_wait=100),
}
