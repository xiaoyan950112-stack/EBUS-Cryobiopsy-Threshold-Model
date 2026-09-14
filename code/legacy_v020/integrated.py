"""Exact event-tree prototype. No clinical inputs are evidence-calibrated.
Costs cover diagnostic resources only, not cancer treatment or therapeutic surgery.
"""
from dataclasses import dataclass, replace, asdict
import math
from selection_v0_3 import IndexInformation, select

def probability(x):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<=1:
        raise ValueError('invalid probability')

@dataclass(frozen=True)
class State:
    weight: float
    disease: str  # unresolved, benign, other, nsclc
    stage: bool = False
    marker: bool = False
    day: float = 10
    cost: float = 0
    operations: int = 0
    events: float = 0
    ready: float | None = None
    marker_day: float | None = None
    log: tuple = ()
    reserved_operation_day: float | None = None

@dataclass(frozen=True)
class Settings:
    horizon: float = 60
    pathway: str = 'neoadjuvant'
    need_pre_markers: bool = True
    alternative_success: float = .5
    alternative_cost: float = 250
    alternative_days: float = 7
    repeat_uptake: float = .8
    repeat_success: float = .9
    repeat_wait: float = 14
    repeat_report: float = 10
    repeat_cost: float = 6000
    repeat_event: float = .02
    event_cost: float = 3000
    stage_success: float = .85
    # Order: both resolved, stage only, marker only, neither.
    joint: tuple = (.65,.15,.10,.10)
    diagnostic: tuple = (.15,.15,.60,.10)  # benign, other, NSCLC, unresolved
    # Conditional on NSCLC diagnosis at diagnostic rescue: both, stage only,
    # marker only, neither. Default preserves the historical prototype.
    diagnostic_nsclc: tuple = (0,0,0,1)
    surgery_uptake: float = .8
    surgery_wait: float = 14
    surgical_report: float = 10
    surgical_marker_success: float = .9
    surgical_assay_cost: float = 250
    scheduling: str = 'sequential'
    crt_start_wait: float = 7
    crt_duration: float = 42
    crt_completed: float = .9
    crt_nonprogression: float = .8  # conditional on completed CRT

def validate(cfg):
    for k,v in asdict(cfg).items():
        if k in ('pathway','need_pre_markers','joint','diagnostic','diagnostic_nsclc','scheduling'): continue
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
            raise ValueError(k)
    for k in ('alternative_success','repeat_uptake','repeat_success','repeat_event',
              'stage_success','surgery_uptake','surgical_marker_success','crt_completed','crt_nonprogression'):
        probability(getattr(cfg,k))
    for values in (cfg.joint,cfg.diagnostic,cfg.diagnostic_nsclc):
        if len(values)!=4: raise ValueError('four outcome probabilities required')
        for v in values: probability(v)
        if not math.isclose(sum(values),1,abs_tol=1e-10): raise ValueError('outcome mass')
    if cfg.horizon<=0 or cfg.pathway not in ('neoadjuvant','direct_surgery','unresectable_iii'):
        raise ValueError('settings')
    if cfg.pathway=='neoadjuvant' and not cfg.need_pre_markers:
        raise ValueError('prototype neoadjuvant requires defined marker bundle')
    if cfg.scheduling not in ('sequential','parallel_booking'): raise ValueError('scheduling')

def run(initial, cfg=Settings()):
    validate(cfg)
    if not initial or not math.isclose(sum(s.weight for s in initial),1,abs_tol=1e-10):
        raise ValueError('initial mass')
    leaves=[]
    def finish(s):
        if s.weight: leaves.append(s)

    def readiness(s):
        if s.disease!='nsclc': return s
        if s.stage and (s.marker or not cfg.need_pre_markers):
            return replace(s,ready=s.ready if s.ready is not None else s.day)
        return s

    def surgery(s):
        s=readiness(s)
        if cfg.pathway!='direct_surgery' or s.ready is None or s.marker:
            finish(s); return
        # Therapeutic surgery is an actual event, not an automatic biomarker report.
        finish(replace(s,weight=s.weight*(1-cfg.surgery_uptake),log=s.log+('no_surgery',)))
        t=s.ready+cfg.surgery_wait
        yes=replace(s,weight=s.weight*cfg.surgery_uptake)
        if t>cfg.horizon:
            finish(replace(yes,log=yes.log+('surgery_pending',))); return
        yes=replace(yes,cost=yes.cost+cfg.surgical_assay_cost,log=yes.log+(f'surgery@{t:g}',))
        report=t+cfg.surgical_report
        if report>cfg.horizon:
            finish(replace(yes,log=yes.log+('surgical_report_pending',))); return
        for ok,w in ((True,cfg.surgical_marker_success),(False,1-cfg.surgical_marker_success)):
            finish(replace(yes,weight=yes.weight*w,marker=ok,marker_day=report if ok else None,
                           log=yes.log+(f'surgical_marker_{ok}@{report:g}',)))

    def intervention(s,kind,outcomes,continuation):
        finish(replace(s,weight=s.weight*(1-cfg.repeat_uptake),log=s.log+(kind+'_declined',)))
        yes=replace(s,weight=s.weight*cfg.repeat_uptake)
        operation=max(s.day,s.reserved_operation_day) if s.reserved_operation_day is not None else s.day+cfg.repeat_wait
        if operation>cfg.horizon:
            finish(replace(yes,log=yes.log+(kind+'_pending',))); return
        yes=replace(yes,cost=yes.cost+cfg.repeat_cost+cfg.repeat_event*cfg.event_cost,
                    operations=yes.operations+1,events=yes.events+cfg.repeat_event,
                    log=yes.log+(f'{kind}@{operation:g}',))
        report=operation+cfg.repeat_report
        if report>cfg.horizon:
            finish(replace(yes,log=yes.log+(kind+'_report_pending',))); return
        for w,updates in outcomes:
            if w:
                child=replace(yes,weight=yes.weight*w,day=report,reserved_operation_day=None,**updates)
                if child.marker and child.marker_day is None: child=replace(child,marker_day=report)
                continuation(child)

    def after_alternative(s):
        s=readiness(s)
        if s.ready is not None and (cfg.pathway!='unresectable_iii' or s.marker): surgery(s); return
        if not s.stage and not s.marker and (cfg.need_pre_markers or cfg.pathway=='unresectable_iii'):
            outcomes=[(w,dict(stage=a,marker=b)) for w,(a,b) in zip(cfg.joint,((True,True),(True,False),(False,True),(False,False)))]
            # One joint operation; partial resolution persists but no infinite rescue loop.
            intervention(s,'joint_rescue',outcomes,lambda x:surgery(readiness(x)))
        elif not s.stage:
            intervention(s,'stage_rescue',[(cfg.stage_success,dict(stage=True)),(1-cfg.stage_success,{})],surgery)
        else:
            intervention(s,'molecular_rescue',[(cfg.repeat_success,dict(marker=True)),(1-cfg.repeat_success,{})],surgery)

    def nsclc(s):
        s=readiness(s)
        if s.ready is not None and (cfg.pathway!='unresectable_iii' or s.marker): surgery(s); return
        if not s.marker and (cfg.need_pre_markers or cfg.pathway=='unresectable_iii'):
            if not s.stage and cfg.scheduling=='parallel_booking':
                # Necessary staging remains required whether alternative markers succeed or fail.
                # Reserve now; choose stage-only versus joint after actual alternative result.
                # No operation precedes that result; an expired slot is assumed rebookable then.
                s=replace(s,reserved_operation_day=s.day+cfg.repeat_wait,
                          log=s.log+(f'reserve_staging@{s.day:g}',))
            # Alternative assessment precedes elective rescue choice; already known marker
            # and stage reports may have been obtained in parallel (initial day is max).
            yes=replace(s,cost=s.cost+cfg.alternative_cost,
                        log=s.log+(f'alternative@{s.day:g}',),day=s.day+cfg.alternative_days)
            if yes.day>cfg.horizon:
                finish(replace(yes,log=yes.log+('alternative_pending',))); return
            for ok,w in ((True,cfg.alternative_success),(False,1-cfg.alternative_success)):
                if w: after_alternative(replace(yes,weight=yes.weight*w,marker=ok,marker_day=yes.day if ok else None))
        else: after_alternative(s)

    def after_diagnostic(s):
        if s.disease=='nsclc': nsclc(s)
        else: finish(s)

    for s in initial:
        probability(s.weight)
        if s.disease not in ('unresolved','benign','other','nsclc'): raise ValueError('disease')
        if s.day<0 or not math.isfinite(s.day): raise ValueError('day')
        if s.disease!='nsclc' and (s.stage or s.marker): raise ValueError('NSCLC-only flags')
        if s.day>cfg.horizon:
            finish(replace(s,disease='unresolved',stage=False,marker=False,ready=None,marker_day=None)); continue
        if s.marker and s.marker_day is None: s=replace(s,marker_day=s.day)
        if s.disease=='unresolved':
            outcomes=[(w,dict(disease=d)) for w,d in zip(cfg.diagnostic,('benign','other','nsclc','unresolved')) if d!='nsclc']
            for conditional,(stage,marker) in zip(cfg.diagnostic_nsclc,((True,True),(True,False),(False,True),(False,False))):
                outcomes.append((cfg.diagnostic[2]*conditional,dict(disease='nsclc',stage=stage,marker=marker)))
            intervention(s,'diagnostic_rescue',outcomes,after_diagnostic)
        else: after_diagnostic(s)
    assert math.isclose(sum(s.weight for s in leaves),1,abs_tol=1e-10)
    def total(f): return sum(s.weight*f(s) for s in leaves)
    result=dict(cost=total(lambda s:s.cost),repeat_operations=total(lambda s:s.operations),
                expected_events=total(lambda s:s.events),
                nsclc_ready=total(lambda s:s.disease=='nsclc' and s.ready is not None and s.ready<=cfg.horizon),
                nsclc_marker_complete=total(lambda s:s.disease=='nsclc' and s.marker_day is not None and s.marker_day<=cfg.horizon),
                diagnostic_unresolved=total(lambda s:s.disease=='unresolved'),
                benign_exit=total(lambda s:s.disease=='benign' and s.day<=cfg.horizon),
                other_malignancy_exit=total(lambda s:s.disease=='other' and s.day<=cfg.horizon),
                leaves=[asdict(s) for s in leaves])
    if cfg.pathway=='unresectable_iii':
        # Separate modeled treatment events from diagnostic resource accounting.
        event_rows=[]
        for s in leaves:
            if s.disease!='nsclc' or s.ready is None:
                event_rows.append(dict(weight=s.weight,crt_end=None,postcrt_ready=None,status='not_ready_for_CRT'))
                continue
            start=s.ready+cfg.crt_start_wait
            end=start+cfg.crt_duration
            event_rows.append(dict(weight=s.weight*(1-cfg.crt_completed),crt_end=None,postcrt_ready=None,status='CRT_not_completed'))
            event_rows.append(dict(weight=s.weight*cfg.crt_completed*(1-cfg.crt_nonprogression),crt_end=end,postcrt_ready=None,status='progression_exits_target_postCRT_path'))
            ready=None if s.marker_day is None else max(end,s.marker_day)
            event_rows.append(dict(weight=s.weight*cfg.crt_completed*cfg.crt_nonprogression,crt_end=end,postcrt_ready=ready,status='completed_without_progression',crt_start=start))
        result['postcrt_information_ready']=sum(e['weight'] for e in event_rows if e['postcrt_ready'] is not None and e['postcrt_ready']<=cfg.horizon)
        result['crt_completed_by_horizon']=sum(e['weight'] for e in event_rows if e['crt_end'] is not None and e['crt_end']<=cfg.horizon)
        result['treatment_events']=event_rows
    return result

def strategy(strata,policy='B_molecular',cryo_cost=600,cryo_event=.005,event_cost=3000):
    if not math.isclose(sum(x['weight'] for x in strata),1,abs_tol=1e-10): raise ValueError('stratum mass')
    totals={}; audit=[]
    for x in strata:
        probability(x['weight']); probability(x['delivery'])
        decision=select(x['info'],policy)
        delivery=x['delivery'] if decision['add_cryobiopsy'] else 0
        a=run(x['A'],x['settings']); b=run(x['B'],x['settings']) if delivery else a
        for k in a:
            if k in ('leaves','treatment_events'): continue
            extra={'cost':cryo_cost+cryo_event*event_cost,'expected_events':cryo_event}.get(k,0)
            value=(1-delivery)*a[k]+delivery*(b[k]+extra)
            totals[k]=totals.get(k,0)+x['weight']*value
        audit.append(dict(stratum=x['name'],weight=x['weight'],selection=decision,delivery=delivery,A=a,B_delivered=b))
    return dict(totals=totals,audit=audit)
