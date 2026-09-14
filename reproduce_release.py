"""Run the manuscript release and fail on any reproducibility discrepancy."""
from pathlib import Path
import sys,subprocess,json,hashlib,platform,math,csv
ROOT=Path(__file__).resolve().parent
logs=[]
def run(path):
 p=subprocess.run([sys.executable,str(ROOT/path)],cwd=ROOT,capture_output=True,text=True)
 logs.append(f'RUN {path}\n{p.stdout}\n{p.stderr}')
 (ROOT/'release_validation.log').write_text('\n'.join(logs))
 if p.returncode:raise RuntimeError(f'{path} failed; see release_validation.log')
def near(x,y):
 if not math.isclose(x,y,abs_tol=1e-8,rel_tol=0):raise AssertionError((x,y))
run('code/reproduce_all.py')
run('code/cost_ceiling/analysis.py')
import shutil
for ext in ('png','pdf'):
 shutil.copy2(ROOT/'code/cost_ceiling'/f'cost_ceiling.{ext}', ROOT/f'Figure_S1.{ext}')
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'code/legacy_v020')]
from differential import compare,Rescue as TreeRescue
from cost_ceiling.analysis import ceiling,Rescue as CostRescue
# 9 p values x 3 r values x 3 alternative-success values x 2 B scenarios = 162.
# Stage-only baseline uptake is 0.8 in the original engine and is held fixed here.
checks=0;max_error=0
for p in [i/8 for i in range(9)]:
 for r in [0,.5,1]:
  for alt in [0,.5,1]:
   for differential in [False,True]:
    a=TreeRescue(alternative_success=alt)
    b=TreeRescue(alternative_success=.2,repeat_uptake=1) if differential else a
    h=ceiling(p,r,a=CostRescue(alt,.8),b=CostRescue(b.alternative_success,b.repeat_uptake))
    expected=compare(p,r,a=a,b=b)['delta']['cost']/100
    near(615-h,expected);checks+=1;max_error=max(max_error,abs(615-h-expected))
for alpha,value in [(0,0),(.25,89.65526315789474),(.5,179.31052631578947),(.75,268.9657894736842),(1,358.62105263157895)]:near(ceiling(8/38,alpha*7/8),value)
near(ceiling(.6,.8),934.464)
refs=json.loads((ROOT/'expected/numerical_sha256.json').read_text())
verified={}
for name,reference in refs.items():
 actual=hashlib.sha256((ROOT/'code'/name).read_bytes()).hexdigest()
 if actual!=reference:raise AssertionError(f'Output differs from manuscript reference: {name}')
 verified[name]=actual
rows={}
for name in refs:
 if name.endswith('.csv'):
  with (ROOT/'code'/name).open() as f:rows[name]=sum(1 for _ in csv.DictReader(f))
import numpy,matplotlib
summary={'status':'passed','version':(ROOT/'VERSION').read_text().strip(),'python':platform.python_version(),'platform':platform.system(),'numpy':numpy.__version__,'matplotlib':matplotlib.__version__,'original_tests':30,'supplement_tests':9,'current_integration_comparisons':checks,'maximum_cost_difference_per_patient':max_error,'supplement_table_value_checks':6,'matched_numerical_files':verified,'csv_data_rows':rows,'validation_scope':'Developer-authored internal verification only; no clinical or external validation'}
(ROOT/'release_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
logs.append(json.dumps(summary,indent=2));(ROOT/'release_validation.log').write_text('\n'.join(logs))
print('PASS: 39 tests, 162 integration comparisons, 6 S3 value checks, 5 exact numerical-file matches.')
