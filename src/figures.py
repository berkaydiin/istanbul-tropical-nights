"""Makaledeki şekiller. Çalıştırma: python src/figures.py"""
import pandas as pd, numpy as np, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.grid':True,'grid.color':'#e3e3e3','grid.linewidth':0.6,'axes.edgecolor':'#888','axes.labelcolor':'#333',
                     'xtick.color':'#555','ytick.color':'#555','axes.titleweight':'bold','axes.titlesize':10,'figure.dpi':200,'axes.axisbelow':True})
# Okabe-Ito, fixed order
C = {'era':'#0072B2','sta':'#D55E00','old':'#999999','new':'#0072B2','acc':'#E69F00','g':'#009E73'}

A = pd.read_csv('data/annual_metrics.csv'); M = pd.read_csv('data/monthly_city.csv')
S = pd.read_csv('data/goztepe_station_annual.csv'); H = pd.read_csv('data/jja_hist_city.csv')
c = A[A.pt=='city'].set_index('year')

# ---------- Fig 1: annual TR20, city mean + station ----------
fig, ax = plt.subplots(figsize=(7.2,4.1))
ax.axvspan(1949.5,1978.5,color='#f3f3f3',zorder=0,lw=0)
ax.text(1964,104,'ERA5 ön uzatma dönemi (1950–1978):\ndaha az gözlem, daha düşük güvenilirlik',ha='center',va='top',fontsize=6.5,color='#777')
ax.plot(c.index,c.tr20,color=C['era'],lw=1.6,label='ERA5-Land, 6 nokta ortalaması (1950–2025)')
ax.plot(S.year,S.tr20,color=C['sta'],lw=1.2,ls='-',alpha=0.9,label='Göztepe istasyonu, GHCN-D (1929–2003)')
# Sen trend 1979-2025
d = c.loc[1979:2025]; sl = stats.theilslopes(d.tr20.values, d.index.values)
xx = np.array([1979,2025]); ax.plot(xx, sl[1]+sl[0]*xx, color=C['era'], lw=1, ls='--', label=f'Sen eğimi 1979–2025: +{sl[0]*10:.1f} gece/10 yıl')
m6190 = c.loc[1961:1990].tr20.mean()
ax.hlines(m6190,1961,1990,color='#333',lw=1,ls=':'); ax.text(1975.5,m6190-6,f'1961–1990 ort. {m6190:.0f}',ha='center',fontsize=7,color='#333')
m1625 = c.loc[2016:2025].tr20.mean()
ax.hlines(m1625,2016,2025,color='#333',lw=1,ls=':'); ax.text(2026,m1625,f'2016–2025\nort. {m1625:.0f}',ha='left',va='center',fontsize=7,color='#333')
ax.annotate('2024: 92',xy=(2024,92),xytext=(2026,96),fontsize=7,arrowprops=dict(arrowstyle='-',color='#555',lw=0.6),color='#333')
ax.set_xlim(1928,2034); ax.set_ylim(0,105); ax.set_ylabel('Tropikal gece sayısı (Tmin > 20 °C), gece/yıl'); ax.set_xlabel('Yıl')
ax.legend(frameon=False,fontsize=7,loc='upper center',bbox_to_anchor=(0.5,-0.16),ncol=2)
fig.tight_layout(); fig.savefig('figures/fig1_tr20_series.png'); plt.close(fig)

# ---------- Fig 2: monthly expansion ----------
fig, ax = plt.subplots(figsize=(5.2,3.0))
mon = ['May','Haz','Tem','Ağu','Eyl','Eki']
p1 = M[(M.year>=1961)&(M.year<=1990)].groupby('m').tr20.mean().reindex(range(5,11))
p2 = M[(M.year>=1996)&(M.year<=2025)].groupby('m').tr20.mean().reindex(range(5,11))
x = np.arange(6); w=0.38
b1=ax.bar(x-w/2,p1.values,w,color=C['old'],label='1961–1990'); b2=ax.bar(x+w/2,p2.values,w,color=C['new'],label='1996–2025')
for xi,v in zip(x-w/2,p1.values): ax.text(xi,v+0.4,f'{v:.1f}',ha='center',fontsize=6.5,color='#333')
for xi,v in zip(x+w/2,p2.values): ax.text(xi,v+0.4,f'{v:.1f}',ha='center',fontsize=6.5,color='#333')
ax.set_xticks(x); ax.set_xticklabels(mon); ax.set_ylabel('Ortalama tropikal gece / ay'); ax.set_ylim(0,31)
ax.legend(frameon=False,fontsize=7); ax.grid(axis='x',visible=False)
fig.tight_layout(); fig.savefig('figures/fig2_monthly.png'); plt.close(fig)

# ---------- Fig 3: decadal share of JJA nights above thresholds ----------
fig, ax = plt.subplots(figsize=(5.2,3.0))
sh=[]
for dec,g in H.groupby('dec'):
    tot=g['count'].sum(); sh.append((dec,g[g.bin>=20]['count'].sum()/tot*100,g[g.bin>=22]['count'].sum()/tot*100,g[g.bin>=24]['count'].sum()/tot*100))
sh=pd.DataFrame(sh,columns=['dec','g20','g22','g24'])
lab=[f"{int(d)}'ler" if d<2020 else '2020–25' for d in sh.dec]
ax.plot(lab,sh.g20,marker='o',ms=4,color=C['new'],lw=1.8,label='> 20 °C')
ax.plot(lab,sh.g22,marker='s',ms=4,color=C['acc'],lw=1.8,label='> 22 °C')
ax.plot(lab,sh.g24,marker='^',ms=4,color=C['g'],lw=1.8,label='> 24 °C')
for i,(a,b,cc) in enumerate(zip(sh.g20,sh.g22,sh.g24)):
    if i in (0,len(sh)-1):
        ax.text(i,a+2.5,f'{a:.0f}%',ha='center',fontsize=7,color='#333'); ax.text(i,b+2.5,f'{b:.0f}%',ha='center',fontsize=7,color='#333'); ax.text(i,cc+2.5,f'{cc:.0f}%',ha='center',fontsize=7,color='#333')
ax.set_ylabel('Haziran–Ağustos gecelerinin payı (%)'); ax.set_ylim(0,80); ax.tick_params(axis='x',labelsize=7.5)
ax.legend(frameon=False,fontsize=7,title='Tmin eşiği',title_fontsize=7)
fig.tight_layout(); fig.savefig('figures/fig3_distribution.png'); plt.close(fig)

# ---------- Fig 4: spatial points, period means ----------
names={'kadikoy':'Kadıköy/\nÜsküdar','umraniye':'Ümraniye','bakirkoy':'Bakırköy','sariyer':'Sarıyer','pendik':'Pendik','avcilar':'Avcılar'}
pts=[p for p in names if p in set(A.pt)]
m1=[A[(A.pt==p)&(A.year>=1961)&(A.year<=1990)].tr20.mean() for p in pts]
m2=[A[(A.pt==p)&(A.year>=1996)&(A.year<=2025)].tr20.mean() for p in pts]
m3=[A[(A.pt==p)&(A.year>=2016)&(A.year<=2025)].tr20.mean() for p in pts]
fig, ax = plt.subplots(figsize=(6.0,3.0)); x=np.arange(len(pts)); w=0.27
ax.bar(x-w,m1,w,color=C['old'],label='1961–1990'); ax.bar(x,m2,w,color='#56B4E9',label='1996–2025'); ax.bar(x+w,m3,w,color=C['new'],label='2016–2025')
for xi,v in zip(x-w,m1): ax.text(xi,v+1,f'{v:.0f}',ha='center',fontsize=6.5,color='#333')
for xi,v in zip(x,m2): ax.text(xi,v+1,f'{v:.0f}',ha='center',fontsize=6.5,color='#333')
for xi,v in zip(x+w,m3): ax.text(xi,v+1,f'{v:.0f}',ha='center',fontsize=6.5,color='#333')
ax.set_xticks(x); ax.set_xticklabels([names[p] for p in pts],fontsize=7.5); ax.set_ylabel('Ortalama tropikal gece / yıl'); ax.set_ylim(0,95)
ax.legend(frameon=False,fontsize=7,ncol=3,loc='upper left'); ax.grid(axis='x',visible=False)
fig.tight_layout(); fig.savefig('figures/fig4_spatial.png'); plt.close(fig)
print('figures done')
