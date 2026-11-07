"""Kuantil delta eşleme (quantile delta mapping, Cannon vd. 2015), toplamsal sürüm, aylık.

Gözlenen 1996-2025 günlük Tmin serisindeki her gün için:
  1. Günün kendi takvim ayındaki gözlem dağılımında yüzdeliği (tau) bulunur.
  2. Modelin aynı aydaki tarihsel (1996-2025) ve gelecek dağılımlarının tau yüzdelikleri alınır.
  3. Aradaki fark (gelecek - tarihsel) gözlenen değere eklenir.
Böylece gözlenen günlük değişkenlik korunur, modelin ortalama ve uçlardaki değişimi aktarılır.

Kullanım:
  proj = qdm(obs, mod_hist, mod_fut)   # her biri tarih indeksli, 'tmin' sütunlu DataFrame
"""
import numpy as np
import pandas as pd


def qdm(obs, mod_hist, mod_fut):
    obs = obs.copy()
    obs.index = pd.to_datetime(obs.index)
    mh = mod_hist.copy(); mh.index = pd.to_datetime(mh.index)
    mf = mod_fut.copy(); mf.index = pd.to_datetime(mf.index)
    out = obs.tmin.copy()
    for m in range(1, 13):
        o = obs.tmin[obs.index.month == m]
        h = mh.tmin[mh.index.month == m].dropna().values
        f = mf.tmin[mf.index.month == m].dropna().values
        # gözlem içindeki yüzdelik (ortalama sıralama, 0-1 aralığı)
        tau = (o.rank(method='average').values - 0.5) / len(o)
        delta = np.quantile(f, tau) - np.quantile(h, tau)
        out[o.index] = o.values + delta
    return out


def simple_delta(obs, mod_hist, mod_fut):
    """Karşılaştırma: yalnızca aylık ortalama farkı ekler."""
    obs = obs.copy(); obs.index = pd.to_datetime(obs.index)
    mh = mod_hist.copy(); mh.index = pd.to_datetime(mh.index)
    mf = mod_fut.copy(); mf.index = pd.to_datetime(mf.index)
    d = mf.tmin.groupby(mf.index.month).mean() - mh.tmin.groupby(mh.index.month).mean()
    return obs.tmin + obs.index.month.map(d).values


if __name__ == '__main__':
    # Sentetik sınama: model her yüzdelikte tam +1,5 °C ısınıyorsa QDM de +1,5 eklemeli
    rng = np.random.default_rng(0)
    idx = pd.date_range('1996-01-01', '2025-12-31')
    obs = pd.DataFrame({'tmin': 15 + 8 * np.sin(2 * np.pi * idx.dayofyear / 365) + rng.normal(0, 2, len(idx))}, index=idx)
    hist = pd.DataFrame({'tmin': obs.tmin.values - 1.0 + rng.normal(0, 0.1, len(idx))}, index=idx)
    fut = pd.DataFrame({'tmin': hist.tmin.values + 1.5}, index=idx + pd.DateOffset(years=40))
    p = qdm(obs, hist, fut)
    print('ortalama eklenen değişim:', round((p - obs.tmin).mean(), 3), '(beklenen 1,5)')
