"""Incremental implementation wrapper. All example inputs are hypothetical."""
from dataclasses import dataclass
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'legacy_v020'))
from reproduce import outcomes, METRICS


def number(x, name, maximum=None):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 or (maximum is not None and x > maximum):
        raise ValueError(name)


@dataclass(frozen=True)
class Stratum:
    name: str
    weight: float
    rose: str = 'concern'
    current_need: bool = True
    suspected_malignancy: bool = True
    # Analytic label only, NEVER used by the selection rule.
    target_nsclc: bool = True
    feasible: float = 1.0
    attempt: float = 1.0  # conditional on feasibility and trigger
    completion: float = 1.0  # conditional on attempt
    p: float = .6
    r: float = .8


@dataclass(frozen=True)
class Implementation:
    screening_cost: float = 0.0  # incremental cost per all-cohort patient
    fixed_cost: float = 0.0  # allocated to this modeled cohort, not per patient
    aborted_cost: float = 100.0
    aborted_events: float = .001
    event_cost: float = 3000.0


def evaluate(strata, config=Implementation(), n=100, outcome_fn=outcomes):
    strata = list(strata)
    number(n, 'n')
    if not strata or not math.isclose(sum(s.weight for s in strata), 1.0, abs_tol=1e-10, rel_tol=0):
        raise ValueError('weights must sum to one')
    if len({s.name for s in strata}) != len(strata):
        raise ValueError('unique stratum names required')
    for k, v in vars(config).items():
        number(v, k, 1 if k == 'aborted_events' else None)
    rows = []
    total = dict.fromkeys(MR := tuple(METRICS), 0.0)
    total['cost'] = n * config.screening_cost + config.fixed_cost
    for s in strata:
        for k in ('weight', 'feasible', 'attempt', 'completion', 'p', 'r'):
            number(getattr(s, k), k, 1)
        if s.rose not in ('concern', 'no_concern', 'unknown'):
            raise ValueError('rose')
        if any(type(getattr(s, k)) is not bool for k in ('current_need', 'suspected_malignancy', 'target_nsclc')):
            raise ValueError('boolean fields')
        count = n * s.weight
        trigger = s.rose == 'concern' and s.current_need and s.suspected_malignancy
        attempts = count * s.feasible * s.attempt if trigger else 0.0
        completed = attempts * s.completion
        aborted = attempts - completed
        delta = dict.fromkeys(MR, 0.0)
        if s.target_nsclc:
            per100 = outcome_fn(s.p, s.r)['delta']
            delta = {k: completed * per100[k] / 100 for k in MR}
        else:
            # Zero incremental diagnostic benefit SCENARIO, not clinical evidence.
            delta['cost'] = completed * 615.0
            delta['expected_events'] = completed * .005
        delta['cost'] += aborted * (config.aborted_cost + config.aborted_events * config.event_cost)
        delta['expected_events'] += aborted * config.aborted_events
        for k in MR:
            total[k] += delta[k]
        rows.append(dict(name=s.name, patients=count, triggered=count if trigger else 0,
                         completed=completed, aborted=aborted,
                         no_attempt=count-attempts, delta=delta))
    return dict(denominator=n, status='HYPOTHETICAL; incremental molecular-policy implementation only',
                overhead_cost=n*config.screening_cost+config.fixed_cost,
                delta=total, strata=rows)
