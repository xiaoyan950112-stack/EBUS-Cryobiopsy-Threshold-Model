"""Reproduce the manuscript calculations, 30 tests and Figure 1."""
from pathlib import Path
import subprocess, sys, json, hashlib, platform
ROOT = Path(__file__).resolve().parent
logs = []
for script in ('legacy_v020/reproduce.py', 'run_differential.py', 'make_figure.py'):
    result = subprocess.run([sys.executable, str(ROOT/script)], cwd=ROOT,
                            capture_output=True, text=True)
    logs.append(f'RUN {script}\n{result.stdout}\n{result.stderr}')
    if result.returncode:
        (ROOT/'validation_log.txt').write_text('\n'.join(logs))
        raise SystemExit(result.returncode)
(ROOT/'validation_log.txt').write_text('\n'.join(logs))
import numpy, matplotlib
files = sorted(p for p in ROOT.rglob('*') if p.suffix in ('.py','.json','.csv') and p.name!='reproduction_manifest.json')
manifest = {'python':platform.python_version(), 'numpy':numpy.__version__,
            'matplotlib':matplotlib.__version__, 'tests':30,
            'status':'Primary/implementation inputs hypothetical; S3 evidence and assumptions documented separately; no clinical validation',
            'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(ROOT/'reproduction_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Completed: 7 conditional + 23 implementation/rescue tests; numerical results and Figure 1.')
