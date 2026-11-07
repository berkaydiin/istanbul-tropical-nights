"""Ana istatistikler: eğilimler (Mann-Kendall + Sen), dönem ortalamaları, Pettitt, istasyon karşılaştırması.
Çalıştırma (depo kök dizininden): python src/analysis.py
"""
import pandas as pd, numpy as np, json
import pymannkendall as mk
from scipy import stats

A = pd.read_csv('data/annual_metrics.csv')
M = pd.read_csv('data/monthly_city.csv')
S = pd.read_csv('data/goztepe_station_annual.csv')
H = pd.read_csv('data/jja_hist_city.csv')

out = {}
pts = ['city','kadikoy','umraniye','bakirkoy','sariyer','pendik','avcilar']

def trend(y, x):
    r = mk.original_test(y)
    sen = stats.theilslopes(y, x)  # slope, intercept, lo, hi (95%)
    return dict(tau=round(r.Tau,3), p=float(r.p), z=round(r.z,2), slope_per_decade=round(r.slope*10,2),
                sen_lo=round(sen[2]*10,2), sen_hi=round(sen[3]*10,2), trend=r.trend)

# 1. Trends 1950-2025 for city and points, several metrics
res = {}
for p in pts:
    d = A[A.pt==p].sort_values('year')
    res[p] = {}
    for col in ['tr20','tr22','tn_jja','tnx','maxrun20','su30','tx_jja','tn_ann']:
        res[p][col] = trend(d[col].values, d.year.values)
    # season length (last20-first20) for years with any TR20
    dd = d.dropna(subset=['first20','last20'])
    res[p]['season_len'] = trend((dd.last20-dd.first20).values, dd.year.values)
    res[p]['first20'] = trend(dd.first20.values, dd.year.values)
    res[p]['last20'] = trend(dd.last20.values, dd.year.values)
out['trends_1950_2025'] = res

# 2. Period means (city)
c = A[A.pt=='city'].set_index('year')
periods = {'1950-1979':(1950,1979),'1961-1990':(1961,1990),'1991-2020':(1991,2020),'1980-2009':(1980,2009),'2010-2025':(2010,2025),'2016-2025':(2016,2025)}
pm = {}
for k,(a,b) in periods.items():
    s = c.loc[a:b]
    pm[k] = dict(tr20=round(s.tr20.mean(),1), tr22=round(s.tr22.mean(),1), tn_jja=round(s.tn_jja.mean(),2),
                 maxrun20=round(s.maxrun20.mean(),1), su30=round(s.su30.mean(),1),
                 season_len=round((s.last20-s.first20).mean(),1), first20=round(s.first20.mean(),1), last20=round(s.last20.mean(),1),
                 tr20_sd=round(s.tr20.std(),1))
out['period_means_city'] = pm

# Welch t-test & Mann-Whitney 1961-1990 vs 1996-2025
a = c.loc[1961:1990].tr20.values; b = c.loc[1996:2025].tr20.values
out['compare_6190_vs_9625'] = dict(mean_a=round(a.mean(),1), mean_b=round(b.mean(),1), ratio=round(b.mean()/a.mean(),2),
    welch_p=float(stats.ttest_ind(a,b,equal_var=False).pvalue), mw_p=float(stats.mannwhitneyu(a,b).pvalue))

# 3. Top years
out['top10_tr20_city'] = c.tr20.sort_values(ascending=False).head(10).to_dict()
out['top10_share_post2010'] = int((c.tr20.sort_values(ascending=False).head(10).index>=2010).sum())
out['years_ge70'] = sorted([int(y) for y in c.index[c.tr20>=70]])
out['years_le30'] = sorted([int(y) for y in c.index[c.tr20<=30]])

# 4. Monthly expansion: mean TR20 per month by period
mm = {}
for k,(a_,b_) in {'1961-1990':(1961,1990),'1996-2025':(1996,2025)}.items():
    s = M[(M.year>=a_)&(M.year<=b_)].groupby('m').tr20.mean().round(1)
    mm[k] = s.to_dict()
out['monthly_tr20_means'] = mm
# share of TR20 nights outside JJA
for k,(a_,b_) in {'1961-1990':(1961,1990),'1996-2025':(1996,2025)}.items():
    s = M[(M.year>=a_)&(M.year<=b_)]
    tot = s.tr20.sum(); outside = s[(s.m<6)|(s.m>8)].tr20.sum()
    out['share_outside_JJA_'+k] = round(outside/tot,3)
# June and September trends
for mo in [6,9]:
    s = M[M.m==mo].sort_values('year')
    out[f'trend_month{mo}'] = trend(s.tr20.values, s.year.values)

# 5. Spatial: period means per point
sp = {}
for p in pts[1:]:
    d = A[A.pt==p].set_index('year')
    sp[p] = dict(m6190=round(d.loc[1961:1990].tr20.mean(),1), m9625=round(d.loc[1996:2025].tr20.mean(),1),
                 m1625=round(d.loc[2016:2025].tr20.mean(),1), slope=res[p]['tr20']['slope_per_decade'], p=res[p]['tr20']['p'])
out['spatial'] = sp

# 6. Station cross-check 1950-2003 (Goztepe vs ERA5-Land kadikoy cell & city)
k = A[A.pt=='kadikoy'].set_index('year'); cc = A[A.pt=='city'].set_index('year')
S2 = S[(S.year>=1950)&(S.year<=2003)].set_index('year')
r_k = stats.pearsonr(S2.tr20, k.loc[1950:2003].tr20); r_c = stats.pearsonr(S2.tr20, cc.loc[1950:2003].tr20)
r_sp = stats.spearmanr(S2.tr20, k.loc[1950:2003].tr20)
out['station_check'] = dict(pearson_kadikoy=round(r_k[0],3), p=float(r_k[1]), pearson_city=round(r_c[0],3), spearman_kadikoy=round(r_sp[0],3),
    station_trend_1950_2003=trend(S2.tr20.values, S2.index.values), era5_kadikoy_trend_1950_2003=trend(k.loc[1950:2003].tr20.values, k.loc[1950:2003].index.values),
    station_trend_1929_2003=trend(S[S.year<=2003].tr20.values, S[S.year<=2003].year.values),
    station_mean_6190=round(S2.loc[1961:1990].tr20.mean(),1), station_mean_9403=round(S2.loc[1994:2003].tr20.mean(),1),
    era5_kad_mean_6190=round(k.loc[1961:1990].tr20.mean(),1), era5_kad_mean_9403=round(k.loc[1994:2003].tr20.mean(),1),
    station_tnjja_corr=round(stats.pearsonr(S2.tn_jja, k.loc[1950:2003].tn_jja)[0],3),
    bias_tnjja=round((k.loc[1950:2003].tn_jja - S2.tn_jja).mean(),2))

# 7. Distribution shift from histogram
def pct(dec):
    h = H[H.dec==dec]; tot=h['count'].sum()
    return dict(gt20=round(h[h.bin>=20]['count'].sum()/tot,3), gt22=round(h[h.bin>=22]['count'].sum()/tot,3), gt24=round(h[h.bin>=24]['count'].sum()/tot,3))
out['hist_shares'] = {int(d):pct(d) for d in sorted(H.dec.unique())}

# 8. Change-point (Pettitt) on city TR20
def pettitt(x):
    # U_t = sum_{i<=t} sum_{j>t} sign(x_i - x_j); K = max|U_t|; p ~ 2 exp(-6K^2/(n^3+n^2))
    x = np.asarray(x); n = len(x)
    Ut = np.array([np.sign(x[:t+1,None]-x[None,t+1:]).sum() for t in range(n-1)])
    kidx = int(np.argmax(np.abs(Ut))); Kst = abs(Ut[kidx])
    p = 2*np.exp(-6*Kst**2/(n**3+n**2))
    return kidx, Kst, p
ki, K, p = pettitt(c.tr20.values)
out['pettitt_city_tr20'] = dict(change_year=int(c.index[ki]), K=int(K), p=float(p),
    mean_before=round(c.tr20.loc[:c.index[ki]].mean(),1), mean_after=round(c.tr20.loc[c.index[ki]+1:].mean(),1))

# 9. Linear OLS for comparison
sl = stats.linregress(c.index.values, c.tr20.values)
out['ols_city_tr20'] = dict(slope_per_decade=round(sl.slope*10,2), p=float(sl.pvalue), r2=round(sl.rvalue**2,3))
# post-1990 trend
cc2 = c.loc[1990:]
out['trend_city_tr20_1990_2025'] = trend(cc2.tr20.values, cc2.index.values)
cc3 = c.loc[1950:1989]
out['trend_city_tr20_1950_1989'] = trend(cc3.tr20.values, cc3.index.values)

# 10. Ratio of TR20 slope to Tn_jja slope: nights per 1C
out['nights_per_degC'] = round(res['city']['tr20']['slope_per_decade']/res['city']['tn_jja']['slope_per_decade'],1)
# OLS of TR20 on tn_jja
sl2 = stats.linregress(c.tn_jja.values, c.tr20.values)
out['tr20_vs_tnjja'] = dict(slope=round(sl2.slope,1), r2=round(sl2.rvalue**2,3))

json.dump(out, open('results/results.json','w'), indent=1, default=float)
print('results/results.json yazıldı')
