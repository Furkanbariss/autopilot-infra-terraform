# ADR-0008: Autoscaler'ın Lambda'ya Taşınması

## Durum
Kabul edildi

## Bağlam
Autoscaler başlangıçta local'de bir Python scripti (`while True` döngüsü) olarak geliştirildi ve test edildi. Ancak gerçek bir sistem, geliştiricinin laptop'una bağımlı olamaz.

## Değerlendirilen Seçenekler
1. **Local script (mevcut)** — geliştirme için uygun ama üretim için değil
2. **Sürekli çalışan EC2/ECS task** — mümkün ama sürekli çalışan kaynak maliyeti
3. **Lambda + EventBridge** — serverless, periyodik tetikleme

## Karar
Autoscaler, AWS Lambda'ya taşındı ve EventBridge ile 2 dakikada bir tetiklenecek şekilde yapılandırıldı.

## Gerekçe
- **Otonomi:** Sistem hiçbir yerel bağımlılık olmadan tamamen cloud'da çalışır
- **Maliyet:** Sürekli çalışan sunucu yerine, yalnızca tetiklendiğinde çalışan serverless
- **Doğal cooldown:** EventBridge'in 2 dk aralığı, stateless yapıda doğal bir cooldown sağlar

## Mimari Dönüşüm
- `while True` döngü → tek seferlik `lambda_handler`
- CSV audit log → CloudWatch Logs (print otomatik gider)
- State'li cooldown → stateless (EventBridge aralığı)

## IAM Least-Privilege
Lambda'ya yalnızca gereken izinler verildi:
- `cloudwatch:GetMetricStatistics`
- `ecs:DescribeServices`, `ecs:UpdateService` — **yalnızca tek bir ECS service'e** kısıtlı (Resource-level)

## Sonuçlar
- Sistem tamamen otonom ve sunucusuz çalışıyor — laptop'a bağımlılık ortadan kalktı
- "AutoPilot Infra" ismi tam anlamıyla doğru hale geldi
- **Gelecek iyileştirme:** Stateless cooldown, DynamoDB'de son aksiyon zamanı tutularak daha hassas hale getirilebilir
