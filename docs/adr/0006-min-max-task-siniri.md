# ADR-0006: MIN/MAX Task Sınırı

## Durum
Kabul edildi

## Bağlam
Autoscaler, `desired_count`'u dinamik olarak değiştiriyor. Bir bug ya da anormal metrik durumunda sınırsız ölçeklendirme riski var.

## Karar
Ölçeklendirmeye sabit sınırlar konuldu: MIN_TASKS = 1, MAX_TASKS = 4.

## Gerekçe
- **Maliyet koruması:** Sınır olmadan, "sürekli scale up" üreten bir hata onlarca task açıp faturayı patlatabilir
- **Kararlılık:** MIN=1, servisin asla tamamen kapanmamasını garantiler
- **Öngörülebilir üst sınır:** MAX=4, en kötü senaryoda maliyetin bilinen bir tavanı olmasını sağlar

## Sonuçlar
- `update_desired_count()` fonksiyonu, istenen değeri her zaman [MIN, MAX] aralığına kırpar
- Anormal metrik senaryolarında maliyet patlaması önlendi
- Bu, "sistemlerin patlayabileceğini biliyorum ve maliyet bilincim var" mesajının somut kanıtı
