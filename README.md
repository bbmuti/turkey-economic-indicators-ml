# Türkiye Ekonomik Göstergeler Tahmini

Türkiye'nin kişi başına düşen gelir ve işsizlik oranı verilerini zaman sırasını koruyarak inceleyen, doğrusal regresyonla temel bir tahmin karşılaştırması üreten makine öğrenmesi çalışmasıdır.

> Bu proje eğitim ve portföy amaçlıdır. Sonuçlar ekonomik veya finansal tavsiye değildir.

## Kapsam

- Ülke: Türkiye (`TUR`)
- Veri kaynağı: World Bank Open Data, SDMX CSV
- Göstergeler: kişi başına gelir ve toplam işsizlik oranı
- Eğitim dönemi: 2000–2020
- Test dönemi: 2021–2024
- Model: basit doğrusal regresyon
- Metrikler: R² ve RMSE

Eğitim ve test dönemleri birbirinden tamamen ayrıdır. Böylece aynı yılın hem model eğitiminde hem de performans ölçümünde kullanılması engellenir.

## Kurulum ve çalıştırma

Python 3.10 veya üzeri önerilir.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python linear_regression_forecast.py
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python linear_regression_forecast.py
```

Program `data/` altındaki tüm CSV dosyalarını işler ve sonuçları `output/` klasörüne yazar.

## Proje yapısı

```text
.
├── data/                              # World Bank SDMX CSV verileri
├── output/                            # Grafik, tahmin ve metrik çıktıları
├── linear_regression_forecast.py      # Veri hazırlama, model ve görselleştirme
├── requirements.txt                   # Python bağımlılıkları
└── README.md
```

## Üretilen çıktılar

Her gösterge için:

- `*_predictions.csv`: yıl, gerçek değer, tahmin ve hata
- `*_forecast.png`: eğitim değerleri ile test gerçek/tahmin grafiği
- `metrics.txt`: dönem bilgileri, R² ve RMSE

Son çalıştırmadaki test sonuçları:

| Gösterge | R² | RMSE |
|---|---:|---:|
| Kişi başına gelir | 0.147471 | 2058.823576 |
| İşsizlik oranı | -3.472065 | 2.768387 |

Negatif R², doğrusal modelin ilgili test döneminde yalnızca ortalama değeri kullanan temel yaklaşımdan daha zayıf kaldığını gösterir. Bu sonuç saklanmış veya olduğundan iyi gösterilmiş değildir; projenin temel modelinin sınırını açıkça ortaya koyar.

## Yöntem

Model yalnızca yılı bağımsız değişken olarak kullanır:

$$
y = \beta_0 + \beta_1 x
$$

Kod şu adımları uygular:

1. SDMX sütunlarını ve Türkiye verisini doğrular.
2. Yıl ve gözlem değerlerini sayısal biçime dönüştürür.
3. 2000–2020 döneminde modeli eğitir.
4. 2021–2024 döneminde daha önce görülmemiş yılları tahmin eder.
5. Tahmin tablosunu, grafikleri ve metrikleri yeniden üretir.

## Sınırlılıklar ve geliştirme alanları

- Tek açıklayıcı değişken olarak yıl kullanıldığı için ekonomik dinamikler bütünüyle temsil edilmez.
- Krizler, politika değişiklikleri ve yapısal kırılmalar doğrusal modelde ayrıca ele alınmaz.
- Test dönemi dört gözlemden oluştuğu için metrikler oynaktır.
- Gelecek çalışmalarda enflasyon, büyüme ve işgücüne katılım gibi değişkenler; zaman serisi çapraz doğrulaması; ARIMA/SARIMA ve ağaç tabanlı modeller karşılaştırılabilir.

Çalışma, Birleşmiş Milletler Sürdürülebilir Kalkınma Amaçları içindeki **SKA 8: İnsana Yakışır İş ve Ekonomik Büyüme** bağlamında temel bir veri analizi örneği olarak hazırlanmıştır.
