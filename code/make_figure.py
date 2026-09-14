from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'legacy_v020'))
from reproduce import outcomes, threshold
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
x=np.linspace(0,1,101)
z=np.array([[outcomes(p,r)['delta']['cost']/1000 for p in x] for r in x])
fig,ax=plt.subplots(figsize=(8,6.5))
im=ax.pcolormesh(x,x,z,cmap='RdBu_r',vmin=-140,vmax=140,shading='auto')
ax.contour(x,x,z,levels=[0],colors='black',linewidths=2)
for rel,style,label in [('lower','--','Minimum overlap'),('upper',':','Maximum overlap')]:
    ax.plot(x,[np.nan if (v:=threshold(p,rel)) is None else v for p in x],style,color='#555555',label=label)
ax.plot([],[],color='black',label='Independent overlap (primary)')
ax.set(xlabel='Baseline molecular failure probability p',ylabel='Relative failure reduction r',xlim=(0,1),ylim=(0,1),title='Conditional cost-neutral thresholds\nAll inputs hypothetical')
ax.legend(loc='lower left',fontsize=9)
fig.colorbar(im,ax=ax,label='Incremental cost per 100 conditional patients\n(thousands of illustrative dollars)')
fig.text(.08,.035,'TBNA-established target NSCLC; trigger eligible and feasible; complete add-on delivery.\n120 days; staging insufficiency 30%. Colors indicate cost differences, not a recommendation.',fontsize=9)
fig.subplots_adjust(bottom=.19)
for ext in ('png','pdf'):
    fig.savefig(ROOT.parent/f'Figure_1.{ext}',dpi=300)
