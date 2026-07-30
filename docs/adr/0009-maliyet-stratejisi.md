# ADR-0009: Maliyet Optimizasyon Stratejisi

## Durum
Kabul edildi

## Bağlam
Cloud maliyetleri kontrolsüz bırakıldığında hızla büyür. Bir DevOps sisteminin maliyet farkındalığı olması beklenir (FinOps).

## Karar
AWS Cost Explorer tabanlı bir maliyet raporlama ve idle kaynak tespit botu geliştirildi.

## Gerekçe
- **Görünürlük:** Servis bazlı maliyet raporu, harcamanın nereye gittiğini gösterir
- **Optimizasyon:** Idle kaynak tespiti (bağlı olmayan volume/IP, durmuş instance) "sessiz para yakan" kaynakları yakalar
- **Farkındalık:** Maliyet konuşabilen bir mühendis, doğrudan paraya dokunduğu için değerlidir

## Teknik Not
Cost Explorer API yalnızca `us-east-1` bölgesinde çalışır — altyapı `eu-north-1`'de olsa bile. Bu tuzak kodda dikkate alındı.

## Sonuçlar
- Haftalık markdown maliyet raporu üretilebiliyor
- Idle kaynaklar (unattached EBS, unassociated Elastic IP, stopped instance) tespit ediliyor
- **Gelecek iyileştirme:** Rapor botu, Lambda + EventBridge (haftalık cron) ile otomatik tetiklenip SNS ile email gönderebilir
