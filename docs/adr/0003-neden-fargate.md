# ADR-0003: Compute için ECS Fargate

## Durum
Kabul edildi

## Bağlam
Container'lar bir yerde çalıştırılmalı. Sunucu yönetimi (EC2) mi, yoksa serverless (Fargate) mi kullanılacağına karar verilmeli.

## Değerlendirilen Seçenekler
1. **EC2 üzerinde container** — tam kontrol ama sunucu yönetimi (patch, ölçekleme, bakım) gerektirir
2. **ECS Fargate** — serverless, sunucu yönetimi yok
3. **EKS (Kubernetes)** — güçlü ama bu ölçek için aşırı karmaşık

## Karar
ECS Fargate seçildi.

## Gerekçe
- **Sunucu yönetimi yok:** Altyapı (host makine) yönetimiyle uğraşılmaz, AWS halleder
- **Ölçeklendirme kolaylığı:** `desired_count` değiştirerek task sayısı ayarlanır
- **Uygun karmaşıklık:** Bu proje ölçeği için Kubernetes gereksiz karmaşıklık getirirdi
- **Maliyet:** Kullanılan kaynak kadar ödeme (küçük task boyutlarıyla ekonomik)

## Sonuçlar
- Uygulama, host yönetimi olmadan serverless çalışıyor
- Self-healing yerleşik geliyor (task ölürse Service yenisini başlatır)
- Autoscaling, `desired_count` üzerinden basitçe uygulanabiliyor
