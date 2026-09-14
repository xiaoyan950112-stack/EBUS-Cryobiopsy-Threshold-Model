# Selective add-on mediastinal cryobiopsy threshold model

Version 1.0.0 reproduces the manuscript primary analysis, population implementation, differential rescue and Supplement S3 conditional cost ceilings. This deterministic event tree is an exploratory cost-consequence threshold analysis. Primary and implementation inputs are hypothetical. S3 uses Fan material-suitability counts and bronchoscopic time with unvalidated endpoint translation and hypothetical costs/rescue. No clinical calibration or external validation is claimed.

## Run

Use Python 3.12 (tested) in a new virtual environment. From the extracted package directory:

    python -m venv .venv
    .venv/bin/python -m pip install -r requirements-lock.txt
    .venv/bin/python reproduce_release.py

On Windows, use .venv\Scripts\python.exe instead. A nonzero exit means a computation, test or reference-output check failed. Installation requires access to the Python package index; model reproduction itself needs no network. Outputs are written into `code/`; Figure 1 and Figure S1 are also exported as PNG and PDF files in the repository root. No random seed is needed.

The entry point runs 30 original tests, 9 supplementary tests, and 162 executable integration comparisons over documented p/r/uptake/rescue combinations. It checks five numerical output files against hashes of the preceding manuscript package and checks the reported S3 table values. These are developer-authored internal checks, not external validation. Figure rendering can vary with fonts and platform; numerical references are checked independently.

## Analysis boundaries

The primary endpoint is the specified EGFR/ALK decision-report bundle with a separate staging-information state; diagnosis is conditioned on initially TBNA-established target NSCLC. On-site selection uses only information available at the time. The conditional denominator assumes complete delivery; the first-EBUS implementation denominator includes non-target and undelivered cases. S3 ceilings are per completed add-on conditional patient. Suitability is not report completion. Diagnostic overlap and trial adverse events are contextual evidence, not model inputs. Monetary inputs are illustrative with no empirical price year. No patient records or copyrighted source PDFs are included.

See MANUSCRIPT_MAP.md for outputs and parameter locations, VERIFICATION.md for the release verification record, and RELEASE_STATUS.md for archival status.

## Creator, license and citation

- Creator: Linjie Yan
- ORCID: https://orcid.org/0009-0002-1572-4047
- Affiliation: Division of Pulmonary, Critical Care and Sleep Medicine, University at Buffalo, Buffalo, NY, USA
- GitHub: https://github.com/xiaoyan950112-stack
- Repository name: `EBUS-Cryobiopsy-Threshold-Model`
- Repository URL: https://github.com/xiaoyan950112-stack/EBUS-Cryobiopsy-Threshold-Model
- Version: 1.0.0
- License: MIT (see LICENSE)
- Copyright: 2026 Linjie Yan

Cite this software using CITATION.cff: Yan, Linjie. Selective add-on mediastinal cryobiopsy threshold model (version 1.0.0).

This repository contains the finalized v1.0.0 code prepared for archival release. A version-specific Zenodo DOI will be added after the GitHub v1.0.0 release is archived. SHA256SUMS.json covers the files in the prepared v1.0.0 package except itself.
