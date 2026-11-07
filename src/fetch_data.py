"""Ham günlük verileri Open-Meteo'dan indirip yıllık göstergeleri hesaplar.

Kaynaklar:
  - ERA5-Land (0,1°) ve ERA5 (0,25°): https://archive-api.open-meteo.com/v1/archive
  - CMIP6 HighResMIP: https://climate-api.open-meteo.com/v1/climate

Open-Meteo'nun ücretsiz arayüzünde dakikalık/saatlik istek sınırı vardır; script
istekler arasında bekler ve hata alırsa yeniden dener. İndirilen günlük seriler
raw/ klasörüne kaydedilir (bu klasör depoya eklenmez).

Örnek kullanım (depo kök dizininden):
  python src/fetch_data.py --start 1950-01-01 --end 2025-12-31
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

import pandas as pd

from indices import annual_indices, humidity_classes

ARCHIVE = 'https://archive-api.open-meteo.com/v1/archive'
CLIMATE = 'https://climate-api.open-meteo.com/v1/climate'

# Makaledeki Tablo 1: altı ERA5-Land noktası (enlem, boylam, yükseklik m).
# Yükseklik Open-Meteo'ya 'elevation' olarak verilir; arayüz sıcaklığı bu yüksekliğe göre düzeltir.
POINTS = {
    'avcilar': (41.0, 28.7, 89),
    'bakirkoy': (41.0, 28.9, 29),
    'sariyer': (41.2, 29.1, 42),
    'kadikoy': (41.0, 29.0, 10),
    'umraniye': (41.0, 29.1, 131),
    'pendik': (40.9, 29.3, 74),
}
CMIP6_MODELS = ['CMCC_CM2_VHR4', 'EC_Earth3P_HR', 'FGOALS_f3_H', 'HiRAM_SIT_HR',
                'MPI_ESM1_2_XR', 'MRI_AGCM3_2_S', 'NICAM16_8S']


def get_json(url, params, tries=6):
    q = url + '?' + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(q, timeout=120) as r:
                return json.load(r)
        except Exception as e:  # sınır aşımı (429) veya ağ hatası
            wait = 65 * (i + 1)
            print(f'  hata: {e}; {wait} sn bekleniyor')
            time.sleep(wait)
    raise RuntimeError('İndirme başarısız: ' + q)


def era5_daily(lat, lon, elev, start, end, model='era5_land', dew=False):
    daily = ['temperature_2m_min', 'temperature_2m_max'] + (['dew_point_2m_mean'] if dew else [])
    j = get_json(ARCHIVE, dict(latitude=lat, longitude=lon, elevation=elev, start_date=start, end_date=end,
                               daily=','.join(daily), models=model, timezone='Europe/Istanbul'))
    d = pd.DataFrame(j['daily']).rename(columns={'time': 'date', 'temperature_2m_min': 'tmin',
                                                 'temperature_2m_max': 'tmax', 'dew_point_2m_mean': 'dew'})
    return d.set_index('date')


def cmip6_daily(lat, lon, model, start='1979-01-01', end='2050-12-31'):
    j = get_json(CLIMATE, dict(latitude=lat, longitude=lon, start_date=start, end_date=end,
                               models=model, daily='temperature_2m_min'))
    d = pd.DataFrame(j['daily']).rename(columns={'time': 'date', 'temperature_2m_min': 'tmin'})
    return d.set_index('date')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', default='1950-01-01')
    ap.add_argument('--end', default='2025-12-31')
    ap.add_argument('--cmip6', action='store_true', help='CMIP6 günlük serilerini de indir')
    a = ap.parse_args()
    os.makedirs('raw', exist_ok=True)

    series = {}
    for name, (lat, lon, elev) in POINTS.items():
        print('ERA5-Land', name)
        series[name] = era5_daily(lat, lon, elev, a.start, a.end)
        series[name].to_csv(f'raw/era5land_{name}.csv')
        time.sleep(10)

    # Kent ortalaması: altı noktanın günlük değerlerinin aritmetik ortalaması
    city = sum(s[['tmin', 'tmax']] for s in series.values()) / len(series)
    city.to_csv('raw/era5land_city.csv')

    tables = []
    for name, s in list(series.items()) + [('city', city)]:
        t = annual_indices(s)
        t.insert(0, 'pt', name)
        tables.append(t)
    pd.concat(tables).to_csv('raw/annual_metrics_recomputed.csv', index=False)
    print('raw/annual_metrics_recomputed.csv yazıldı (data/annual_metrics.csv ile karşılaştırılabilir)')

    # Nem: 1979 sonrası çiy noktası
    dews = [era5_daily(lat, lon, elev, '1979-01-01', a.end, dew=True) for lat, lon, elev in POINTS.values()]
    city_dew = sum(d[['tmin', 'dew']] for d in dews) / len(dews)
    humidity_classes(city_dew).to_csv('raw/humidity_city_recomputed.csv', index=False)

    if a.cmip6:
        for m in CMIP6_MODELS:
            print('CMIP6', m)
            cmip6_daily(41.0, 29.0, m).to_csv(f'raw/cmip6_{m}.csv')
            time.sleep(10)


if __name__ == '__main__':
    main()
