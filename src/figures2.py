"""Makaledeki şekiller. Çalıştırma: python src/figures2.py"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':'#e3e3e3','grid.linewidth':0.6,'axes.edgecolor':'#888','axes.labelcolor':'#333','xtick.color':'#555','ytick.color':'#555','figure.dpi':200,'axes.axisbelow':True})
H=pd.read_csv('data/humidity_city.csv').set_index('year')
# Fig 5: stacked bars: dry tropical nights, muggy (18-20), oppressive (>=20)
fig,ax=plt.subplots(figsize=(7.0,3.3))
dry=H.tr20_dry; m18=H.muggy18-H.muggy20; m20=H.muggy20
ax.bar(H.index,dry,color='#BBBBBB',width=0.8,label='Kuru (çiy noktası < 18 °C)')
ax.bar(H.index,m18,bottom=dry,color='#56B4E9',width=0.8,label='Nemli (18–20 °C)')
ax.bar(H.index,m20,bottom=dry+m18,color='#0072B2',width=0.8,label='Boğucu (≥ 20 °C)')
ax.set_ylabel('Tropikal gece sayısı (gece/yıl)'); ax.set_xlabel('Yıl'); ax.set_xlim(1978,2026); ax.set_ylim(0,100)
ax.legend(frameon=False,fontsize=7,loc='upper left',title='Gece ortalaması çiy noktasına göre',title_fontsize=7); ax.grid(axis='x',visible=False)
fig.tight_layout(); fig.savefig('figures/fig5_humidity.png'); plt.close(fig)
print('fig5 ok')

import os
if os.path.exists('data/cities.csv'):
    Cc=pd.read_csv('data/cities.csv'); A=pd.read_csv('data/annual_metrics.csv'); ist=A[(A.pt=='city')&(A.year>=1979)][['year','tr20']].assign(city='istanbul')
    allc=pd.concat([ist,Cc[['city','year','tr20']]])
    names={'istanbul':'İstanbul','izmir':'İzmir','antalya':'Antalya','bursa':'Bursa','ankara':'Ankara'}
    cols={'istanbul':'#0072B2','izmir':'#E69F00','antalya':'#D55E00','bursa':'#009E73','ankara':'#CC79A7'}
    fig,ax=plt.subplots(figsize=(7.0,3.4))
    for c in ['antalya','izmir','istanbul','bursa','ankara']:
        d=allc[allc.city==c].sort_values('year'); y=d.tr20.rolling(5,center=True).mean()
        ax.plot(d.year,y,color=cols[c],lw=1.8,label=names[c]); ax.text(2026,y.iloc[-3],names[c],color=cols[c],fontsize=7.5,va='center')
    ax.set_xlim(1979,2031); ax.set_ylabel('Tropikal gece (5 yıllık hareketli ort.)'); ax.set_xlabel('Yıl'); ax.legend(frameon=False,fontsize=7,loc='upper left',ncol=5)
    fig.tight_layout(); fig.savefig('figures/fig7_cities.png'); plt.close(fig); print('fig7 ok')
if os.path.exists('data/cells.csv'):
    K=pd.read_csv('data/cells.csv'); yrs=[str(y) for y in range(1979,2026)]
    K['m7998']=K[[str(y) for y in range(1979,1999)]].mean(axis=1); K['m0625']=K[[str(y) for y in range(2006,2026)]].mean(axis=1); K['m1625']=K[[str(y) for y in range(2016,2026)]].mean(axis=1)
    K['slope']=[stats.theilslopes(r[yrs].values.astype(float),np.arange(1979,2026))[0]*10 for _,r in K.iterrows()]
    K['diff']=K.m0625-K.m7998
    tr={'Adalar/Maltepe':'Adalar, Maltepe','Arnavutkoy':'Arnavutköy','Atasehir/Kadikoy/Umraniye':'Ataşehir, Kadıköy, Ümraniye','Avcilar/Esenyurt':'Avcılar, Esenyurt',
        'Bagcilar/Bahcelievler/Bakirkoy/Esenler/Gungoren/Zeytinburnu':'Bakırköy, Bağcılar, Bahçelievler (+3)','Basaksehir':'Başakşehir','Bayrampasa/Eyupsultan/Gaziosmanpasa/Sultangazi':'Eyüpsultan, Gaziosmanpaşa (+2)',
        'Besiktas/Kagithane/Sisli':'Beşiktaş, Kâğıthane, Şişli','Beykoz':'Beykoz','Beylikduzu/Buyukcekmece':'Beylikdüzü, Büyükçekmece','Beyoglu/Fatih/Uskudar':'Beyoğlu, Fatih, Üsküdar',
        'Catalca':'Çatalca','Cekmekoy/Sancaktepe':'Çekmeköy, Sancaktepe','Sariyer':'Sarıyer','Kartal/Pendik':'Kartal, Pendik','Kucukcekmece':'Küçükçekmece','Silivri':'Silivri','Sultanbeyli':'Sultanbeyli','Sile':'Şile','Tuzla':'Tuzla'}
    K=K.sort_values('m1625'); y=np.arange(len(K))
    fig,ax=plt.subplots(figsize=(7.0,5.4))
    ax.hlines(y,K.m7998,K.m1625,color='#cccccc',lw=2,zorder=1)
    ax.scatter(K.m7998,y,color='#999999',s=36,zorder=2,label='1979–1998')
    ax.scatter(K.m1625,y,color='#0072B2',s=36,zorder=3,label='2016–2025')
    for yi,(a,b,el) in enumerate(zip(K.m7998,K.m1625,K.elev)): ax.text(b+1.5,yi,f'{b:.0f}',va='center',fontsize=7,color='#333'); ax.text(a-1.5,yi,f'{a:.0f}',va='center',ha='right',fontsize=7,color='#777')
    ax.set_yticks(y); ax.set_yticklabels([f"{tr.get(d,d)} ({'kıyı' if int(e)==0 else str(int(e))+' m'})" for d,e in zip(K.districts,K.elev)],fontsize=7.5)
    ax.set_xlabel('Ortalama tropikal gece / yıl'); ax.set_xlim(15,98); ax.grid(axis='y',visible=False)
    ax.legend(frameon=False,fontsize=7.5,loc='lower right')
    fig.tight_layout(); fig.savefig('figures/fig6_cells.png'); plt.close(fig); print('fig6 ok')
    K.to_csv('data/cells_summary.csv',index=False)

if os.path.exists('data/cmip6_projection.csv'):
    P=pd.read_csv('data/cmip6_projection.csv'); A=pd.read_csv('data/annual_metrics.csv'); c=A[(A.pt=='city')&(A.year>=1979)].set_index('year')
    fig,ax=plt.subplots(figsize=(7.0,3.5))
    ax.plot(c.index,c.tr20,color='#0072B2',lw=1.6,label='Gözlenen (ERA5-Land kent ortalaması)')
    base=c.loc[1996:2025].tr20.mean()
    ax.hlines(base,1996,2025,color='#333',ls=':',lw=1); ax.text(1996,base+3,f'1996–2025 ort. {base:.0f}',ha='left',fontsize=7,color='#333')
    for w,x,col in [('2021-2050',2034,'#56B4E9'),('2036-2050',2043,'#D55E00')]:
        g=P[P.window==w]; med=g.qdm_tr20.median()
        ax.vlines(x,g.qdm_tr20.min(),g.qdm_tr20.max(),color=col,lw=6,alpha=0.35)
        ax.scatter([x]*len(g),g.qdm_tr20,color=col,s=14,zorder=3,edgecolor='white',linewidth=0.4)
        ax.hlines(med,x-1.4,x+1.4,color=col,lw=2.2)
        R=lambda v: f'{np.floor(v+0.5):.0f}'
        ax.text(x+2.2,med,f'{w.replace("-","–")}\nmedyan {R(med)}\n({R(g.qdm_tr20.min())}–{R(g.qdm_tr20.max())})',fontsize=6.8,va='center',color='#333',bbox=dict(facecolor='white',edgecolor='none',pad=1))
    ax.annotate('2024: 92',xy=(2024,92),xytext=(2013,99),fontsize=7,arrowprops=dict(arrowstyle='-',color='#555',lw=0.6),color='#333')
    ax.axvline(2025.5,color='#bbb',lw=0.8); ax.text(2026.2,12,'projeksiyon\n(7 CMIP6 modeli,\nSSP5-8.5)',fontsize=6.5,color='#777',va='bottom')
    ax.set_xlim(1978,2054); ax.set_ylim(0,108); ax.set_ylabel('Tropikal gece sayısı (gece/yıl)'); ax.set_xlabel('Yıl')
    ax.legend(frameon=False,fontsize=7,loc='upper left')
    fig.tight_layout(); fig.savefig('figures/fig8_projection.png'); plt.close(fig); print('fig8 ok')
