# Conditional add-on cost ceilings

This module implements supplementary conditional cost ceilings. It uses published suitability/time evidence with unvalidated endpoint translation and hypothetical rescue and monetary assumptions. It is not a calibrated economic effect estimate. Run ../../reproduce_release.py for the full package.

## Denominator and axis

Every ceiling is per conditional target patient receiving a completed add-on procedure. These are not per-100-first-EBUS policy ceilings. The analysis excludes non-target recipients, abandoned procedures, incomplete delivery and screening costs; those require the existing population implementation layer before drawing policy conclusions.

The horizontal axis u is the probability of invasive rescue among patients still missing required information after alternative testing. It is not the probability of repeat biopsy among all index EBUS patients or all initially molecular-insufficient patients. In molecular-only failures, the unconditional repeat probability is (1-a)u. Patients still requiring staging can undergo a procedure even when molecular testing succeeds. For compatibility with the original simplified model, the same u is used for staging-only rescue. No benefit is assigned to correcting a molecular deficit when it cannot remove the need for a staging procedure, except avoidance of the modeled alternative assay cost.

All modeled rescue procedures occur within the observation window. There is no apparent saving from moving procedures outside the horizon. Operation cost is incurred irrespective of eventual rescue success; hence lower success alone does not alter this one-procedure cost ceiling, although it changes clinical outcomes. Time-to-report and clinical outcome comparisons remain outside this module.

## Inputs

| Input | Value | Status |
|---|---:|---|
| Original required-report illustration: p, r | 0.60, 0.80 | Hypothetical legacy inputs |
| Suitability-based illustration: proxy p, r | 8/38, 7/8 | Derived from Fan counts with an explicit no-loss and full endpoint-translation assumption |
| Staging insufficiency g | 0, 0.30, 0.60; 1 in grid | Hypothetical |
| Joint insufficiency j | p*g for plotted curves | Independence assumption; function also accepts feasible j |
| Alternative testing cost L | 250 | Hypothetical dollars |
| Alternative testing success a | 0.50 | Hypothetical |
| Repeat procedure cost | 6,000 | Hypothetical dollars |
| Expected repeat-event cost | 0.02*3,000 = 60 | Hypothetical, generic severity |
| Total expected repeat cost C | 6,060 | Hypothetical dollars |
| Differential-rescue illustration | aB=0.20; uB=min(1,uA+0.20) | Hypothetical; distinct from changing rescue success |
| Between-arm difference in mean total bronchoscopic procedure duration | 5.3 minutes | Fan: 22.3 minus 17.0 minutes; insertion to removal, not full room occupancy |
| Minute price, extra pathology, probe price | Unestimated | Variables, not measured costs |

Source for suitability counts and procedure time: [Fan et al.](https://doi.org/10.1016/S2213-2600(22)00392-7), main report and supplementary protocol sections 4.4–4.8 and 6. Four TBNA passes plus one cryobiopsy were compared with four TBNA passes; ROSE was not used. The original suitability paragraph reports 30/38 versus 37/38. Exact report completion, the candidate concern rule and the specified EGFR/ALK report bundle were not validated by those counts.

## Derivation

Let H be the total expected incremental cost of performing the add-on, including consumables, time, extra pathology and expected add-on harm costs. Define downstream costs for complete information, molecular-only deficit, staging-only deficit and joint deficit as:

- Complete: 0.
- Molecular only: L+(1-a)uC.
- Staging only: uC.
- Both: L+uC.

Under equal rescue, the maximum H consistent with cost neutrality is:

Hmax = r[(p-j){L+(1-a)uC} + jL].

With j=pg this becomes:

Hmax = pr[L+(1-g)(1-a)uC].

Incremental strategy cost is H-Hmax. A negative Hmax is not set to zero: it means no nonnegative add-on cost achieves neutrality under the modeled pathway assumptions. At u=0 there can still be a positive ceiling from avoided alternative tests. That does not imply avoided invasive procedures.

For unequal rescue, the module directly weights state-specific A and B downstream costs. Initially molecular-complete/staging-incomplete B states retain A rescue, matching the existing differential-rescue implementation. Changing B rescue can produce cost differences even at r=0; these are attributed to management assumptions, not sampling benefit. No claim is made that this additive 20-percentage-point uptake difference is observed or universally pessimistic.

## Main numerical results

The following table uses g=0.30 and equal rescue unless otherwise stated.

| u: uptake after alternatives fail | Hypothetical report Hmax | Full-translation suitability Hmax | Hypothetical report Hmax with different rescue |
|---:|---:|---:|---:|
| 0% | 120.00 | 46.05 | -5.08 |
| 25% | 374.52 | 143.73 | 211.26 |
| 50% | 629.04 | 241.41 | 427.61 |
| 75% | 883.56 | 339.09 | 643.95 |
| 80% | 934.46 | 358.62 | 687.22 |
| 100% | 1,138.08 | 436.76 | 985.37 |

These columns are different analytical scenarios, not competing estimates of one empirical population. The second column retains legacy report assumptions. The third uses suitability failures as a proxy baseline and assumes the suitability improvement translates completely into report improvement. It must not be presented as an observed economic effect of Fan's intervention.

## Endpoint-translation sensitivity

For a transparent stress test, hold the proxy baseline p=8/38 fixed and replace r=7/8 by alpha*(7/8). Alpha is the assumed fraction of the suitability improvement translating to the modeled report benefit, not a measured probability. It does not resolve baseline endpoint mismatch, subset selection, assay differences or confounding by staging needs. Therefore this sensitivity is not a validation bridge and is not a substitute for report-completion data.

At u=0.80, g=0.30 and equal rescue:

| Assumed translation alpha | Total expected add-on ceiling |
|---:|---:|
| 0 | 0.00 |
| 0.25 | 89.66 |
| 0.50 | 179.31 |
| 0.75 | 268.97 |
| 1.00 | 358.62 |

No confidence intervals or credible regions are inferred from these values. Full translation is the most favorable bridge in this defined range, not a proven clinical upper bound across all possible workflows.

## From total ceiling to a probe/consumable budget

The 5.3-minute input is the between-arm difference in mean total bronchoscopic procedure duration, measured from bronchoscope insertion to removal (Fan supplementary protocol section 4.5). It is not isolated cryobiopsy time or total room occupancy including preparation and recovery. The trial used a high-frequency electric needle knife to establish access before cryobiopsy (section 4.4). The combined probe/access-consumable budget therefore includes the needle knife and associated access consumables. A probe-only budget requires subtracting access costs as well. Access time already represented in the total bronchoscopic duration must not be added again; any additional preparation, recovery or equipment allocation requires separate justification. Other access techniques require their own resource assumptions.

The graph shows Hmax, not an acceptable probe purchase price. Subtract all other additional components:

Maximum probe/access-consumable budget = Hmax - 5.3*c_minute - extra pathology - expected add-on event cost - other incremental costs.

For an explicitly hypothetical illustration, c_minute=10, extra pathology=50, expected add-on event cost=15 and other costs=0 leave a probe/access budget of 240.62 from the full-translation Hmax of 358.62. At alpha=0.50, the remaining budget is only 61.31. These are not supplier quotes, charges or hospital cost estimates. If the residual budget is negative, no nonnegative consumable price meets neutrality under those settings.

The 15 event-cost assumption is inherited as 0.005*3,000. It is not Fan's measured incremental bleeding cost. Use a consistent provider-resource perspective for this component calculation. Do not mix a Medicare payment rate into the staff/room resource price or add packaged charges twice. If capital/equipment costs are allocated, record the volume and allocation method rather than silently setting them to zero.

## Figure and reproduction

`cost_ceiling.png` contains two explicitly separated panels. Solid curves vary staging insufficiency; dashed curves vary B rescue. Panel B is an unvalidated endpoint-translation illustration. All panels use illustrative costs.

The complete release entry point runs nine supplementary tests alongside the original 30 tests and 162 executable event-tree comparisons. See ../../release_verification.json and ../../release_validation.log for current results and scope. Tests remain developer-authored internal verification.

## Interpretation and next boundary

The model now supplies a reviewable cost ceiling instead of requiring an invented add-on price. It explicitly shows why higher repeat uptake raises the ceiling, unresolved staging reduces it, and different residual-failure management can lower it. The result is still only partially evidence-anchored: the trial informs suitability counts and time, while costs, rescue and endpoint translation remain hypothetical.

The analysis is integrated in Supplement S3. The original report endpoint, model code and numerical outputs remain unchanged after review of the Fan appendix. Trial adverse events and diagnostic overlap are contextual evidence only.
