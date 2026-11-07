# İstanbul'da Tropikal Geceler, 1950–2025

Bu depo, aşağıdaki kongre bildirisinin verilerini, analiz kodunu ve şekillerini içerir:

> Aydın, M. B. (2026). *İstanbul'da tropikal geceler ikiye katlandı: 1950–2025 dönemi için ERA5-Land ve istasyon verilerine dayalı bir değerlendirme.* Uluslararası Sürdürülebilir Su Yönetimi ve İklim Değişikliği Kongresi, Fırat Üniversitesi, Elazığ, 11–14 Kasım 2026.

**Yazar:** Mustafa Berk Aydın, Üsküdar Amerikan Lisesi · ORCID [0009-0003-6296-3910](https://orcid.org/0009-0003-6296-3910)

[English summary below](#english)

## Ana bulgular

| | Değer |
|---|---|
| Tropikal gece (Tmin > 20 °C), kent ortalaması, 1961–1990 | 37 gece/yıl |
| Aynı gösterge, 2016–2025 | 75 gece/yıl |
| Rekor yıl | 2024, 92 gece |
| Eğilim, 1979–2025 (Sen eğimi) | on yılda +12,3 gece (%95 GA 10,0–14,3) |
| Kırılma yılı (Pettitt) | 2000 |
| Göztepe istasyonu ile korelasyon, 1979–2003 | r = 0,90 |
| CMIP6 projeksiyonu, 2036–2050 (7 model, SSP5-8.5) | medyan 91 gece/yıl (83–95) |

## Klasörler

```
data/       Yıllık ve aylık gösterge tabloları (CSV); sütun açıklamaları data/README.md'de
src/        Analiz ve şekil kodları
results/    Kodların ürettiği sayısal sonuçlar (JSON)
figures/    Bildirideki 8 şekil
paper/      Bildirinin tam metni (Word)
```

## Sonuçları yeniden üretmek

Python 3.10 veya üstü gerekir.

```bash
pip install -r requirements.txt
python src/analysis.py        # eğilimler, dönem ortalamaları, Pettitt, istasyon karşılaştırması
python src/analysis_extra.py  # nem, ilçe hücreleri, diğer kentler, ERA5, projeksiyon özeti, maruziyet
python src/figures.py         # Şekil 1–4
python src/figures2.py        # Şekil 5–8
```

Bu dört script yalnızca `data/` klasöründeki tabloları kullanır, internet bağlantısı gerektirmez. Bildirideki bütün sayılar `results/` klasöründeki JSON dosyalarında yer alır.

### Ham veriden başlamak

`src/fetch_data.py`, altı ERA5-Land noktasının günlük Tmin/Tmax değerlerini [Open-Meteo](https://open-meteo.com/) arşiv arayüzünden indirir ve `src/indices.py` ile yıllık göstergeleri hesaplar. `--cmip6` seçeneğiyle yedi HighResMIP modelinin günlük serilerini de indirir. `src/qdm.py` kuantil delta eşleme yönteminin uygulamasıdır.

```bash
python src/fetch_data.py --start 1950-01-01 --end 2025-12-31
```

Birkaç not:

- `data/` klasöründeki tablolar ilk olarak tarayıcı üzerinden yürütülen bir indirme adımıyla üretildi. `fetch_data.py` bu adımın Python karşılığıdır. Kadıköy noktası için 2020–2025 yıllarında ürettiği bütün göstergeler `data/annual_metrics.csv` ile birebir aynıdır. Tam dönem için karşılaştırma henüz yapılmadı.
- Open-Meteo, istenen noktanın yüksekliğine göre sıcaklığı düzeltir. Aynı sonuçları almak için `fetch_data.py` içindeki yükseklik değerleri (Tablo 1) kullanılmalıdır.
- İlçe hücreleri, diğer kentler ve ERA5 (0,25°) serileri aynı arayüzden ve aynı göstergelerle elde edildi, ancak bunların indirme adımı scripte eklenmedi.
- `data/cmip6_projection.csv` içindeki model sonuçları ilk analizde üretildi. `qdm.py` aynı yöntemi uygular ve sentetik veriyle sınandı, ancak bu tablonun uçtan uca yeniden üretimi henüz doğrulanmadı.
- Open-Meteo'nun ücretsiz arayüzünde istek sınırı vardır. Tam indirme saatler sürebilir.

## Veri kaynakları

- **ERA5-Land** (Muñoz-Sabater vd., 2021) ve **ERA5** (Hersbach vd., 2020), Copernicus İklim Değişikliği Servisi. Open-Meteo üzerinden erişildi.
- **CMIP6 HighResMIP** (Haarsma vd., 2016): CMCC-CM2-VHR4, EC-Earth3P-HR, FGOALS-f3-H, HiRAM-SIT-HR, MPI-ESM1.2-XR, MRI-AGCM3.2-S, NICAM16-8S. Open-Meteo iklim arayüzü üzerinden erişildi.
- **Göztepe istasyonu** (WMO 17062), NOAA GHCN-Daily (Menne vd., 2012), istasyon kodu TU000017062.
- **Nüfus:** TÜİK genel nüfus sayımları (1950–2000) ve Adrese Dayalı Nüfus Kayıt Sistemi (2007–2025).

Open-Meteo verileri CC BY 4.0 lisansıyla sunulmaktadır. ERA5 ürünleri Copernicus lisansına tabidir.

## Sınırlılıklar

- 1950–1978 dönemi ERA5'in daha az gözlemle üretilmiş ön uzatmasına dayanır. Ana eğilimler bu yüzden 1979–2025 için verilmiştir.
- GHCN-Daily'de Göztepe istasyonunun 2003 sonrası kaydı yoktur. Son 20 yıl istasyonla doğrulanamamıştır.
- 9 km çözünürlüklü ERA5-Land, kentsel ısı adası etkisini tam olarak yansıtmaz.
- Projeksiyon tek bir senaryoya (SSP5-8.5) dayanır.
- Sağlık etkileri için İstanbul'a özgü veri kullanılmamıştır. Bildiride başka ülkelerdeki çalışmalardan aktarılmıştır.

<!-- Yapay zekâ kullanım beyanı buraya eklenecek -->

## Lisans

Kod [MIT lisansı](LICENSE) ile, `data/` ve `results/` klasörlerindeki türetilmiş tablolar ile `figures/` klasöründeki şekiller [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) lisansı ile paylaşılmaktadır. Kullanırken bildiriye atıf yapınız (bkz. `CITATION.cff`).

---

<a id="english"></a>
## English summary

Data, code and figures for a conference paper on tropical nights (daily minimum temperature above 20 °C) in Istanbul, 1950–2025.

Using ERA5-Land reanalysis at six grid points, the city-average number of tropical nights rose from 37 per year in 1961–1990 to 75 in 2016–2025, with a record 92 in 2024. The 1979–2025 Sen's slope is +12.3 nights per decade (95% CI 10.0–14.3), and a Pettitt test places the change point at 2000. The trend holds in all 20 grid cells covering Istanbul's 39 districts, agrees with the Göztepe station record (r = 0.90, 1979–2003) and with ERA5. Seven bias-corrected CMIP6 HighResMIP models (SSP5-8.5) project a median of 91 tropical nights per year for 2036–2050.

To reproduce all statistics and figures from the tables in `data/`:

```bash
pip install -r requirements.txt
python src/analysis.py && python src/analysis_extra.py && python src/figures.py && python src/figures2.py
```

`src/fetch_data.py` downloads the raw daily series from Open-Meteo and recomputes the annual indices. See the Turkish section above for notes on how far this step has been validated. Code is MIT-licensed; derived tables and figures are CC BY 4.0.
