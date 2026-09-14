"""v0.3 structural module: observable selection and two treatment timelines.
No fitted clinical parameters. Does not simulate complete diagnosis/staging.
"""
from dataclasses import dataclass, asdict
import json
import math
from pathlib import Path

@dataclass(frozen=True)
class IndexInformation:
    optimized_tbna_completed: bool
    suitable_target: bool
    safe_to_add: bool
    diagnostic_concern: bool
    malignant_suspicion: bool
    molecular_material_concern: bool | str
    biomarkers_needed_before_next_treatment: bool
    planned_surgical_tissue_acceptable: bool
    biomarkers_needed_for_future_decision: bool = False

    def __post_init__(self):
        # Explicit states prevent Python truthiness from treating 'unknown' as concern.
        concern = self.molecular_material_concern
        if type(concern) is bool:
            object.__setattr__(self, 'molecular_material_concern',
                               'concern' if concern else 'no_concern')
        elif not isinstance(concern, str) or concern not in ('concern', 'no_concern', 'unknown'):
            raise ValueError('Use concern, no_concern, or unknown')
        for key, value in asdict(self).items():
            if key != 'molecular_material_concern' and type(value) is not bool:
                raise ValueError('Boolean required: ' + key)

def select(info: IndexInformation, policy: str):
    """Only information available before ending the index procedure is allowed.
    Concern variables are observable proxies, never final histology/NGS failure.
    Policies are distinct research alternatives, not clinical recommendations.
    """
    if policy not in ('A', 'B_diagnostic', 'B_molecular', 'B_either'):
        raise ValueError('Unknown policy')
    diagnostic = info.optimized_tbna_completed and info.diagnostic_concern
    molecular = (info.optimized_tbna_completed and info.malignant_suspicion
                 and info.molecular_material_concern == 'concern'
                 and info.biomarkers_needed_before_next_treatment
                 and not info.planned_surgical_tissue_acceptable)
    indication = {'A': False, 'B_diagnostic': diagnostic,
                  'B_molecular': molecular, 'B_either': diagnostic or molecular}[policy]
    deliverable = info.suitable_target and info.safe_to_add
    return {'indication': indication, 'deliverable': deliverable,
            'add_cryobiopsy': indication and deliverable,
            'diagnostic_trigger': diagnostic, 'molecular_trigger': molecular,
            'rose_material_assessment': info.molecular_material_concern,
            'assessment_unresolved': info.molecular_material_concern == 'unknown',
            'current_decision_requires_markers': info.biomarkers_needed_before_next_treatment,
            'future_decision_requires_markers': info.biomarkers_needed_for_future_decision,
            'future_only_need': (info.biomarkers_needed_for_future_decision
                                 and not info.biomarkers_needed_before_next_treatment)}

@dataclass(frozen=True)
class Milestones:
    pathway: str
    diagnosis_day: float | None
    adequate_staging_day: float | None
    pretreatment_biomarkers_required: bool
    required_biomarker_report_day: float | None
    surgery_day: float | None = None
    surgical_report_day: float | None = None
    horizon: float = 60

def timeline(m: Milestones):
    if m.pathway not in ('neoadjuvant', 'direct_surgery'):
        raise ValueError('Unknown pathway')
    for key, value in asdict(m).items():
        if key in ('pathway', 'pretreatment_biomarkers_required') or value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError('Invalid day: ' + key)
    if m.horizon <= 0:
        raise ValueError('Positive horizon required')
    if m.pathway == 'neoadjuvant' and not m.pretreatment_biomarkers_required:
        raise ValueError('This neoadjuvant module requires its prespecified biomarker bundle')
    needed = [m.diagnosis_day, m.adequate_staging_day]
    if m.pretreatment_biomarkers_required:
        needed.append(m.required_biomarker_report_day)
    ready = None if None in needed else max(needed)
    if m.surgery_day is not None:
        if m.pathway != 'direct_surgery' or ready is None or m.surgery_day < ready:
            raise ValueError('Surgery must follow documented readiness in direct-surgery module')
    if m.surgical_report_day is not None:
        if m.surgery_day is None or m.surgical_report_day < m.surgery_day:
            raise ValueError('Surgical report must follow actual surgery')
    # Both report sources must satisfy the same prespecified bundle. No imputation.
    reports = [x for x in (m.required_biomarker_report_day, m.surgical_report_day) if x is not None]
    report = min(reports) if reports else None
    return {'decision_ready_day': ready, 'bundle_report_day': report,
            'decision_ready_by_horizon': ready is not None and ready <= m.horizon,
            'bundle_complete_by_horizon': report is not None and report <= m.horizon,
            'restricted_unresolved_decision_days': min(ready, m.horizon) if ready is not None else m.horizon,
            'note': 'Information readiness only; not actual treatment start or causal treatment delay.'}

def stratified_difference(rows):
    """Externally supplied conditional strategy outcomes, NOT predicted by this module.
    Strata must share a baseline definition across A/B, before cryobiopsy.
    Include trigger+/-, aborted delivery, diagnosis and intended treatment strata.
    """
    if not rows or not math.isclose(sum(r['weight'] for r in rows), 1, abs_tol=1e-10):
        raise ValueError('Weights must sum to one')
    cost = complete = 0.0
    for r in rows:
        for k in ('weight', 'cost_a', 'cost_b', 'completion_a', 'completion_b'):
            if not math.isfinite(r[k]) or r[k] < 0:
                raise ValueError('Invalid stratum value')
        if any(r[k] > 1 for k in ('weight', 'completion_a', 'completion_b')):
            raise ValueError('Probability outside [0,1]')
        cost += r['weight'] * (r['cost_b'] - r['cost_a'])
        complete += r['weight'] * (r['completion_b'] - r['completion_a'])
    return {'incremental_cost': cost, 'incremental_completion': complete,
            'status': 'Algebraic aggregation of supplied conditional outcomes; not calibrated'}

def demonstration():
    info = IndexInformation(True, True, True, False, True, True, True, False)
    return {'status': 'HYPOTHETICAL STRUCTURAL EXAMPLES ONLY',
            'selection': {p: select(info, p) for p in ('A', 'B_diagnostic', 'B_molecular', 'B_either')},
            'neoadjuvant': timeline(Milestones('neoadjuvant', 3, 5, True, 20)),
            'direct_surgery': timeline(Milestones('direct_surgery', 3, 5, False, None, 18, 28)),
            'staging_unresolved': timeline(Milestones('direct_surgery', 3, None, False, 10))}

if __name__ == '__main__':
    out = Path(__file__).with_name('selective_demo.json')
    out.write_text(json.dumps(demonstration(), indent=2) + '\n')
    print(out)
