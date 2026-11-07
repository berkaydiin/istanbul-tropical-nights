# Veri tabloları

Tüm sıcaklıklar °C'dir. "Kent ortalaması", altı ERA5-Land noktasının günlük değerlerinin ortalamasından hesaplanan seridir (`pt = city`).

| Dosya | İçerik |
|---|---|
| `annual_metrics.csv` | 6 nokta + kent ortalaması, yıllık göstergeler, 1950–2025 |
| `monthly_city.csv` | Kent ortalaması, mayıs–ekim arası aylık tropikal gece sayısı ve ortalama Tmin |
| `jja_hist_city.csv` | Haziran–ağustos Tmin değerlerinin on yıllara göre 1 °C'lik histogramı |
| `jja_percentiles_city.csv` | Haziran–ağustos Tmin yüzdelikleri, 30 yıllık dönemler |
| `humidity_city.csv` | Tropikal gecelerin çiy noktasına göre sınıfları, 1979–2025 |
| `cells.csv` | 39 ilçe merkezini içeren 20 ERA5-Land hücresi, yıllık TR20, 1979–2025 |
| `cells_summary.csv` | Aynı hücreler, dönem ortalamaları ve eğilimlerle |
| `cities.csv` | Ankara, İzmir, Bursa, Antalya: yıllık TR20 ve yaz Tmin ortalaması, 1979–2025 |
| `era5_city.csv` | ERA5 (0,25°) kent ortalaması, 1950–2025 |
| `goztepe_station_annual.csv` | Göztepe istasyonu (GHCN-Daily TU000017062), 1929–2003 |
| `cmip6_raw_tr20.csv` | 7 HighResMIP modelinin düzeltilmemiş yıllık TR20 değerleri, 1979–2050 |
| `cmip6_projection.csv` | Kuantil delta eşleme ile düzeltilmiş model sonuçları, 2021–2050 ve 2036–2050 |
| `istanbul_population.csv` | İstanbul il nüfusu, TÜİK |

## `annual_metrics.csv` sütunları

| Sütun | Tanım |
|---|---|
| `tr20`, `tr22`, `tr25` | Tmin > 20, 22, 25 °C olan gece sayısı |
| `tn_jja`, `tx_jja` | Haziran–ağustos ortalama Tmin ve Tmax |
| `tn_ann` | Yıllık ortalama Tmin |
| `tnx` | Yılın en yüksek Tmin değeri |
| `first20`, `last20` | İlk ve son tropikal gecenin yılın kaçıncı günü olduğu |
| `maxrun20` | En uzun kesintisiz tropikal gece dizisi |
| `su30`, `su35` | Tmax ≥ 30 ve ≥ 35 °C olan gün sayısı |

## `humidity_city.csv` sütunları

| Sütun | Tanım |
|---|---|
| `muggy18` | Çiy noktası ≥ 18 °C olan tropikal geceler (nemli) |
| `muggy20` | Çiy noktası ≥ 20 °C olan tropikal geceler (boğucu) |
| `tr20_dry` | Çiy noktası < 18 °C olan tropikal geceler |
| `td_mean_tr` | Tropikal gecelerde ortalama çiy noktası |
| `n_td18` | Çiy noktası ≥ 18 °C olan gün sayısı (tüm günler) |
| `tdjja` | Haziran–ağustos ortalama çiy noktası |

## `goztepe_station_annual.csv` sütunları

`ndays_tmin` ve `ndays_tmax` yıl içindeki geçerli gün sayısını, `ndays_mayoct` mayıs–ekim arasındaki geçerli Tmin günlerini gösterir.
