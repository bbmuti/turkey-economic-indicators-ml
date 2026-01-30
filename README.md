# Turkey Economic Indicators (ML) — Türkiye Ekonomik Göstergeler Tahmini

Bu depo, **Türkiye** için iki temel ekonomik göstergenin yıllara göre değişimini inceleyip **doğrusal regresyon (Linear Regression)** ile kısa vadeli tahminler üretir:

- **Kişi Başı Gelir (GDP per capita)**  
- **İşsizlik Oranı (%)**

Çalışma, **SKA 8: İnsana Yakışır İş ve Ekonomik Büyüme** (Sürdürülebilir Kalkınma Amaçları) perspektifiyle değerlendirilmiştir.

---

## Amaç ve Problem Tanımı

Geçmiş yıllara ait ekonomik göstergeler kullanılarak, bu göstergelerin gelecek yıllarda nasıl bir eğilim izleyeceğini tahmin etmek ve elde edilen bulgular üzerinden sürdürülebilir kalkınma hedeflerine yönelik yorum/öneri sunmaktır.

---

## Veri Kaynağı

Veriler **World Bank Open Data** platformundan alınmıştır ve **SDMX CSV formatındadır**.

- Ülke: **Türkiye (TUR)**
- Zaman aralığı: **2000–2024**
- Frekans: **Yıllık**

> Not: Kod, SDMX formatında şu sütunları bekler: `TIME_PERIOD`, `OBS_VALUE`, `REF_AREA`, `INDICATOR` (varsa `INDICATOR_LABEL`).

---

## Yöntem

Bu projede her gösterge için **ayrı bir Basit Doğrusal Regresyon** modeli kurulmuştur:

\[
y = \beta_0 + \beta_1 x
\]

- **x:** Yıl  
- **y:** Tahmin edilen gösterge (işsizlik oranı veya kişi başı gelir)

### Eğitim / Test Ayrımı (Zaman Sırası Korunur)

Kodda dönemler sabit olarak şu şekilde tanımlıdır:

- **Train (Eğitim): 2000–2020**
- **Test: 2020–2024**

---

## Değerlendirme Metrikleri

Kod yalnızca iki metriği raporlar:

- **R² (Belirlilik Katsayısı)**
- **RMSE (Root Mean Squared Error)**

Her gösterge için metrikler `output/metrics.txt` dosyasına yazılır.

---

## Proje Yapısı

Aşağıdaki yapı, repodaki mevcut dizin yapısı ile uyumludur:

```text
turkey-economic-indicators-ml/
├── data/
│ ├── WB_WDI_NY_GDP_PCAP_CD.csv
│ └── WB_WDI_SL_UEM_TOTL_ZS.csv
├── output/
│ ├── WB_WDI_NY_GDP_PCAP_CD_forecast.png
│ ├── WB_WDI_NY_GDP_PCAP_CD_predictions.csv
│ ├── WB_WDI_SL_UEM_TOTL_ZS_forecast.png
│ ├── WB_WDI_SL_UEM_TOTL_ZS_predictions.csv
│ └── metrics.txt
└── linear_regression_forecast.py
```

---

## Üretilen Çıktılar

Her bir ekonomik gösterge (CSV dosyası) için aşağıdaki çıktılar üretilmektedir:

### 1. Tahmin Tablosu (CSV)
`*_predictions.csv` dosyası aşağıdaki sütunları içerir:
- **Year**: Yıl  
- **Actual**: Gerçek gözlem değeri  
- **Predicted**: Doğrusal regresyon modeli ile tahmin edilen değer  
- **Error**: Tahmin hatası (Predicted − Actual)

### 2. Grafik (PNG)
`*_forecast.png` dosyası, zaman serisini aşağıdaki bileşenlerle görselleştirir:
- **Train (Actual)**: Eğitim dönemine ait gerçek değerler  
- **Test (Actual)**: Test dönemine ait gerçek değerler  
- **Test (Predicted)**: Test dönemi için model tahminleri  

Grafikler, modelin geçmiş eğilimleri ne ölçüde yakalayabildiğini görsel olarak değerlendirmeyi sağlar.

### 3. Performans Metrikleri (TXT)
`metrics.txt` dosyasında her gösterge için aşağıdaki değerlendirme ölçütleri raporlanır:
- **R² (Belirlilik Katsayısı)**
- **RMSE (Root Mean Squared Error)**

---

## Bulguların Kısa Yorumu

Doğrusal regresyon modeli, ekonomik göstergelerin **uzun dönemli genel eğilimlerini** yakalamada kullanılabilir bir yöntem sunmaktadır. Ancak model; **ani ekonomik şoklar**, **yapısal kırılmalar** ve **politika değişiklikleri** gibi faktörleri doğrudan dikkate almamaktadır.

Bu nedenle elde edilen sonuçlar, **trend tabanlı tahminler** olarak yorumlanmalı ve kısa vadeli öngörülerde temkinli kullanılmalıdır.

---

## SKA 8 (İnsana Yakışır İş ve Ekonomik Büyüme) Perspektifi

İşsizlik oranında gözlemlenen yatay ve dönemsel dalgalanmalar, istihdam artışının kendiliğinden gerçekleşmediğini ve **istihdam yaratma kapasitesi yüksek sektörlere yönelik uzun vadeli politikaların** önemini ortaya koymaktadır.

Kişi başı gelirdeki kademeli artış ise ekonomik büyümenin sürdüğünü göstermekle birlikte, **sürdürülebilir refah artışı** için verimlilik odaklı yapısal dönüşümlerin desteklenmesi gerektiğine işaret etmektedir.
