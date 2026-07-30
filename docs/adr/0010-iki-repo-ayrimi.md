# ADR-0010: Uygulama ve Altyapı Kodunun Ayrı Repolarda Tutulması

## Durum
Kabul edildi

## Bağlam
Proje iki farklı türde kod içerir: uygulama kodu (FastAPI servisi) ve altyapı kodu (Terraform, Lambda, monitoring). Bunların aynı repoda mı yoksa ayrı repolarda mı tutulacağına karar verilmeli.

## Değerlendirilen Seçenekler
1. **Tek repo (monorepo)** — her şey bir arada, basit ama uygulama ve altyapı değişiklikleri iç içe geçer
2. **Ayrı repolar** — uygulama ve altyapı bağımsız versiyonlanır

## Karar
İki ayrı repo kullanıldı:
- `autopilot-app` — uygulama (FastAPI, Dockerfile, CI/CD)
- `autopilot-infra-terraform` — altyapı (Terraform, Lambda, monitoring, dokümantasyon)

## Gerekçe
- **Separation of concerns:** Uygulama geliştirme ile altyapı yönetimi farklı sorumluluk alanları — ayrılmaları mantıklı
- **Bağımsız versiyonlama:** Uygulama kodu değiştiğinde altyapı state'i etkilenmez, tersine de öyle
- **Bağımsız deploy:** CI/CD, uygulama reposundaki değişiklikleri altyapıya dokunmadan deploy edebilir
- **Gerçek dünya pratiği:** Birçok ekipte uygulama ve platform/altyapı ekipleri ayrı çalışır, bu ayrım o modele uygundur

## Sonuçlar
- Uygulama değişiklikleri (`autopilot-app`), CI/CD ile altyapıdan bağımsız deploy oluyor
- Altyapı değişiklikleri (`autopilot-infra-terraform`), Terraform ile ayrı yönetiliyor
- İki repo, README üzerinden birbirine referans veriyor

## Not (Gelecek Değerlendirme)
Küçük ölçekli projelerde monorepo da geçerli bir tercihtir; iki repo yaklaşımı, uygulama ve altyapının bağımsız yaşam döngülerine sahip olduğu senaryolarda daha çok fayda sağlar.
