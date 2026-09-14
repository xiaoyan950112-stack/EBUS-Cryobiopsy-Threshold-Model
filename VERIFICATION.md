# Verification of release 1.0.0

A new Python virtual environment without system site packages was created, and dependencies were installed from the package index. On 2026-09-14, the complete entry point was invoked from outside the package directory (/private/tmp), using only the packaged source and installed dependencies. Python 3.12.5 was used with the unchanged requirements-lock.txt; pip check reported no broken requirements. PYTHONDONTWRITEBYTECODE=1 prevented bytecode artifacts, and MPLCONFIGDIR pointed to a temporary cache directory. Python and dependency versions are recorded in release_verification.json and requirements-lock.txt. This v1.0.0 verification was performed on macOS (Darwin). Linux and Windows were not separately tested for this final release.

All 30 original tests and 9 supplementary tests passed. An executable 162-combination comparison against the original event-tree engine passed to an absolute tolerance of 1e-8 illustrative dollars per patient. Six supplementary values (including all five alpha levels at u=0.8) matched the manuscript calculations. Five regenerated numerical files matched the preceding manuscript files byte-for-byte. Data rows: primary grid 30,603; cost-ceiling grid 1,616; translation grid 25. Figure 1 and Figure S1 were regenerated in PNG and PDF formats; the PNG exports were visually inspected. The largest absolute integration difference was 1.3642420526593924e-12 illustrative dollars per patient.

The 162-combination grid is p=0,1/8,...,1; r=0,0.5,1; A alternative success=0,0.5,1; and equal versus differential B rescue. A/staging baseline uptake remains 0.8; differential B uses alternative success 0.2 and uptake 1.0. This is a current documented comparison grid, not a recovered historical test grid. Original clinical model assumptions were not changed.

These results verify implementation and reproducibility for this environment, not empirical accuracy, clinical validity or effectiveness. Creator metadata, the MIT license and CITATION.cff are finalized. External publication and DOI registration remain deferred.


## Package integrity

The supplied archive's SHA256SUMS.json was verified before editing. All 14 packaged Python files, three dependency specifications and three expected-reference files are byte-for-byte unchanged from the supplied archive. CITATION.cff was parsed as YAML and checked for the release version, creator and MIT license. SHA256SUMS.json was regenerated after the final edits and covers all other files in the ZIP, including LICENSE and CITATION.cff. The ZIP itself has a separate SHA-256 sidecar. Reproduction rewrites generated outputs and logs, so hashes of those files may differ on subsequent runs; the five numerical reference hashes must still match.
