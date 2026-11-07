"""Ek istatistikler: 1961 ve 1979 sonrası eğilimler, istasyon karşılaştırması, nem sınıfları,
ilçe hücreleri, diğer kentler, ERA5 karşılaştırması, CMIP6 projeksiyon özeti ve nüfus maruziyeti.
Çalıştırma (depo kök dizininden): python src/analysis_extra.py
"""
import json
import numpy as np
import pandas as pd
import pymannkendall as mk
from scipy import stats

A = pd.read_csv('data/annual_metrics.csv')
S = pd.read_csv('data/goztepe_station_annual.csv').set_index('year')
c = A[A.pt == 'city'].set_index('year')
out = {}


def sen(y, x):
    """Sen eğimi (on yıl başına), %95 güven aralığı ve Mann-Kendall p değeri."""
    s = stats.theilslopes(y, x)
    r = mk.original_test(y)
    return dict(slope=round(s[0] * 10, 2), lo=round(s[2] * 10, 2), hi=round(s[3] * 10, 2),
                p=float(r.p), tau=round(r.Tau, 2))


# 1. Farklı başlangıç yıllarıyla kent ortalaması eğilimleri
for start in (1961, 1979):
    d = c.loc[start:2025]
    res = {col: sen(d[col].values, d.index.values)
           for col in ['tr20', 'tr22', 'tn_jja', 'tnx', 'maxrun20', 'su30', 'tx_jja']}
    dd = d.dropna(subset=['first20', 'last20'])
    res['season_len'] = sen((dd.last20 - dd.first20).values, dd.index.values)
    res['first20'] = sen(dd.first20.values, dd.index.values)
    res['last20'] = sen(dd.last20.values, dd.index.values)
    res['points_tr20'] = {}
    for p in ['kadikoy', 'umraniye', 'bakirkoy', 'sariyer', 'pendik', 'avcilar']:
        q = A[A.pt == p].set_index('year').loc[start:2025]
        res['points_tr20'][p] = sen(q.tr20.values, q.index.values)
    out[f'trends_{start}_2025'] = res

# 2. Göztepe istasyonu ve ERA5-Land kent ortalaması
for a, b in [(1950, 1978), (1979, 2003)]:
    st, ci = S.loc[a:b].tr20, c.loc[a:b].tr20
    out[f'station_vs_city_{a}_{b}'] = dict(pearson=round(stats.pearsonr(st, ci)[0], 2),
                                           station_mean=round(st.mean(), 1), era5land_mean=round(ci.mean(), 1))

# 3. Nem sınıfları (çiy noktası), 1979-1998 ve 2016-2025
Hm = pd.read_csv('data/humidity_city.csv').set_index('year')
out['humidity'] = {k: {col: round(Hm.loc[a:b, col].mean(), 1) for col in ['tr20', 'tr20_dry', 'muggy18', 'muggy20']}
                   for k, (a, b) in {'1979-1998': (1979, 1998), '2016-2025': (2016, 2025)}.items()}

# 4. İlçe hücreleri (20 ERA5-Land hücresi, 39 ilçe merkezi), 1979-2025
K = pd.read_csv('data/cells.csv')
yrs = [str(y) for y in range(1979, 2026)]
x = np.arange(1979, 2026)
K['slope'] = [stats.theilslopes(r[yrs].astype(float).values, x)[0] * 10 for _, r in K.iterrows()]
K['m1625'] = K[[str(y) for y in range(2016, 2026)]].mean(axis=1)
r_el = stats.pearsonr(K.elev, K.m1625)
out['cells'] = dict(n=len(K), slope_min=round(K.slope.min(), 1), slope_max=round(K.slope.max(), 1),
                    coolest=K.loc[K.m1625.idxmin(), 'districts'], coolest_m1625=round(K.m1625.min(), 1),
                    hottest=K.loc[K.m1625.idxmax(), 'districts'], hottest_m1625=round(K.m1625.max(), 1),
                    elev_vs_m1625_r=round(r_el[0], 2), elev_vs_m1625_p=round(r_el[1], 3))

# 5. Diğer büyük kentler (1979-2025)
C = pd.read_csv('data/cities.csv')
cities = {name: sen(g.tr20.values, g.year.values)['slope'] for name, g in C.groupby('city')}
ist = c.loc[1979:2025]
cities['istanbul'] = sen(ist.tr20.values, ist.index.values)['slope']
out['cities_sen_per_decade_1979_2025'] = dict(sorted(cities.items(), key=lambda kv: -kv[1]))

# 6. ERA5 (0,25°) ile ERA5-Land karşılaştırması
E = pd.read_csv('data/era5_city.csv').set_index('year')
e = E.loc[1979:2025]  # eğilim 1979-2025; korelasyon 1950-2025
out['era5'] = dict(sen_1979_2025=sen(e.tr20.values, e.index.values)['slope'],
                   pearson_with_era5land_1950_2025=round(stats.pearsonr(E.tr20, c.loc[1950:2025].tr20)[0], 2))

# 7. CMIP6 HighResMIP projeksiyon özeti (yedi modelin medyanı ve aralığı)
P = pd.read_csv('data/cmip6_projection.csv')
out['projection'] = {w: {col: dict(median=round(g[col].median(), 1), min=round(g[col].min(), 1), max=round(g[col].max(), 1))
                         for col in ['qdm_tr20', 'qdm_tr22', 'qdm_maxrun', 'dJJA', 'delta_tr20']}
                     for w, g in P.groupby('window')}

# 8. Nüfus ağırlıklı maruziyet (kişi-gece); sayım yılları arası doğrusal ara değerleme
pop = pd.read_csv('data/istanbul_population.csv').set_index('year')['pop']
pop = pop.reindex(range(1950, 2026)).interpolate()
expo = c.tr20 * pop.reindex(c.index)
p1625 = pop.loc[2016:2025].mean()
cf = c.loc[1961:1990].tr20.mean() * p1625
out['exposure'] = dict(mean_1961_1990=round(expo.loc[1961:1990].mean() / 1e6), mean_1991_2020=round(expo.loc[1991:2020].mean() / 1e6),
                       mean_2016_2025=round(expo.loc[2016:2025].mean() / 1e6), y2024=round(expo.loc[2024] / 1e6),
                       counterfactual_2016_2025_with_1961_1990_climate=round(cf / 1e6),
                       climate_share=round((expo.loc[2016:2025].mean() - cf) / 1e6), unit='milyon kişi-gece/yıl')

json.dump(out, open('results/results_extra.json', 'w'), indent=1, ensure_ascii=False, default=float)
print('results/results_extra.json yazıldı')
