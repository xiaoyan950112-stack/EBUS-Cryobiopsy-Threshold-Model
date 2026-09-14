# Manuscript and output map

| Manuscript component | Reproduction output or source |
|---|---|
| Tables 1 and 2; primary Results | code/legacy_v020/results.json |
| Full p/r overlap grid | code/legacy_v020/grid.csv (30,603 rows) |
| Figure 1 | Figure_1.png and Figure_1.pdf |
| Table 3 active assumptions | code/legacy_v020/reproduce.py, integrated.py, population.py, differential.py, run_differential.py; primary and implementation inputs remain hypothetical |
| Table 4; implementation; 120/240-day scenarios | code/differential_results.json |
| S3 cost ceilings, Table S4, Figure S1 | code/cost_ceiling/ceiling_grid.csv (1,616 rows), cost_ceiling.png/pdf (also exported as root Figure_S1.png/pdf); stdout in release_validation.log |
| S3 translation sensitivity, Table S5 | code/cost_ceiling/translation_sensitivity.csv (25 rows); manuscript alpha values at u=0.8 independently checked by reproduce_release.py |
| S3 time, access, adverse events and diagnostic overlap | code/cost_ceiling/READ_FIRST.md; these evidence descriptions are not fitted clinical inputs |
| Run environment and verification | release_validation.log and release_verification.json |

Primary legacy directory names preserve imports. Shared engine settings for unused treatment pathways are retained but do not form part of the reported analysis. Parameters remain partly embedded in source code; Table 3 values are not a separate runtime input file. The supplementary module does not model time-to-report outcomes or full-cohort implementation.

## Figure S1 export and audit trail

code/cost_ceiling/analysis.py computes the curves with ceiling() at u=0,0.01,...,1. The same calculations are written to ceiling_grid.csv with endpoint, p, r, g, uptake and rescue-scenario fields. translation_sensitivity.csv separately records the endpoint-translation assumptions. Figure_S1.pdf contains vector lines and text; Figure_S1.png is exported directly at 600 dpi on a 12 x 5.6 inch canvas (7200 x 3360 pixels). At a 7.2-inch placement width, fonts and line widths scale to 60% of their source size; check legibility in the selected journal layout. These are general publication exports, not a claim of compliance with an unspecified journal.

Tables in the manuscript remain native editable Word tables. Their displayed values are rounded from the mapped outputs. An editable table is not itself proof of source validity. Parameters embedded in Python are explicitly identified above; no patient-level data are claimed. S3 trial evidence is contextual and is not substituted for decision-report completion.

Version 1.0.0 finalizes release metadata, licensing and citation and reruns reproduction; all Python source files, clinical model calculations and numerical reference hashes are retained unchanged from the supplied package. SHA256SUMS.json identifies the delivered package contents; release_verification.json records the rerun against the earlier numerical references.
