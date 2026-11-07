"""Günlük Tmin/Tmax serisinden yıllık göstergeler (ETCCDI tanımları).

Girdi: tarih indeksli ve 'tmin', 'tmax' sütunlu (°C) bir pandas DataFrame.
Çıktı: data/annual_metrics.csv ile aynı sütunlara sahip yıllık tablo.
"""
import numpy as np
import pandas as pd


def longest_run(mask):
    """Ardışık True değerlerinin en uzun dizisi."""
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def annual_indices(daily):
    d = daily.copy()
    d.index = pd.to_datetime(d.index)
    rows = []
    for year, g in d.groupby(d.index.year):
        jja = g[g.index.month.isin([6, 7, 8])]
        hot = g.tmin > 20
        doy = g.index.dayofyear[hot.values]
        rows.append(dict(
            year=year,
            tr20=int((g.tmin > 20).sum()),          # tropikal gece
            tr22=int((g.tmin > 22).sum()),
            tr25=int((g.tmin > 25).sum()),
            tn_jja=round(jja.tmin.mean(), 2),       # yaz (Haz-Ağu) ortalama Tmin
            tn_ann=round(g.tmin.mean(), 2),
            tnx=round(g.tmin.max(), 2),             # yılın en yüksek Tmin değeri
            first20=int(doy.min()) if len(doy) else np.nan,
            last20=int(doy.max()) if len(doy) else np.nan,
            maxrun20=longest_run(hot.values),       # en uzun kesintisiz tropikal gece dizisi
            su30=int((g.tmax >= 30).sum()),          # gündüz 30 °C'ye ulaşan gün
            su35=int((g.tmax >= 35).sum()),
            tx_jja=round(jja.tmax.mean(), 2),
        ))
    return pd.DataFrame(rows)


def humidity_classes(daily):
    """Tropikal geceleri günlük ortalama çiy noktasına göre sınıflar (1979 sonrası).
    'tmin' ve 'dew' (°C) sütunları gerekir."""
    d = daily.copy()
    d.index = pd.to_datetime(d.index)
    rows = []
    for year, g in d.groupby(d.index.year):
        tr = g[g.tmin > 20]
        jja = g[g.index.month.isin([6, 7, 8])]
        rows.append(dict(year=year, tr20=len(tr),
                         muggy18=int((tr.dew >= 18).sum()),   # nemli tropikal gece
                         muggy20=int((tr.dew >= 20).sum()),   # boğucu tropikal gece
                         td_mean_tr=round(tr.dew.mean(), 2),
                         tr20_dry=int((tr.dew < 18).sum()),
                         n_td18=int((g.dew >= 18).sum()),
                         tdjja=round(jja.dew.mean(), 2)))
    return pd.DataFrame(rows)
