# Architecture — Sistem Mimarisi

[← Ana sayfaya dön](../README.md)

Bu doküman, AutoPilot Infra'nın katmanlı mimarisini ve bileşenler arası veri akışını açıklar.

---

## Genel Bakış

Sistem beş mantıksal katmandan oluşur:

1. **Uygulama Katmanı** — Kullanıcı isteklerini karşılayan servis
2. **Altyapı Katmanı** — Ağ, yük dengeleme, container orchestration
3. **CI/CD Katmanı** — Otomatik test ve dağıtım
4. **Otomatik Ölçeklendirme Katmanı** — Metrik analizi ve karar üretimi
5. **Gözlemlenebilirlik & Maliyet Katmanı** — İzleme, uyarı, raporlama

---

## Katman 1: Uygulama Katmanı

**Bileşen:** FastAPI tabanlı bir web servisi, Docker container'ı olarak paketlenmiş.

> **Repo:** Uygulama kodu ayrı bir repoda tutulur → [autopilot-app](https://github.com/Furkanbariss/autopilot-app) (FastAPI + Dockerfile + CI/CD workflow). Bu ayrımın gerekçesi için bkz. [ADR-0010](adr/0010-iki-repo-ayrimi.md).

**Endpoint'ler:**
- `/` — temel durum kontrolü
- `/health` — ALB health check hedefi (200 döner)
- `/compute` — kontrollü CPU yükü üreten endpoint (yük testi ve autoscaling tetikleme için)
- `/light` — hafif referans işlem

`/compute` endpoint'i, `iterations` parametresiyle CPU yükünü ayarlanabilir kılar — bu, farklı yük senaryolarını (düşük/orta/yüksek) simüle etmeyi sağlar.

---

## Katman 2: Altyapı Katmanı

Tüm altyapı Terraform ile tanımlıdır (bkz. [infrastructure.md](infrastructure.md)).

**Ağ:**
- **VPC** (`10.0.0.0/16`) — izole ağ ortamı
- **Public subnet'ler** (2 farklı AZ) — ALB ve Fargate task'ları için
- **Internet Gateway + Route Table** — dış erişim yönlendirmesi

**Yük Dengeleme:**
- **Application Load Balancer (ALB)** — gelen trafiği Fargate task'larına dağıtır
- **Target Group** (IP-tabanlı) — `/health` üzerinden health check yapar

**Container Orchestration:**
- **ECS Cluster** (Fargate) — serverless container çalıştırma
- **Task Definition** — container yapılandırması (image, CPU/memory, port, log)
- **ECS Service** — istenen task sayısını sürekli koruyan yönetici katman (self-healing)
- **ECR** — Docker image deposu

---

## Katman 3: CI/CD Katmanı

**GitHub Actions** ile üç aşamalı pipeline (bkz. [cicd.md](cicd.md)):

```
git push (main)
   │
   ├─→ test           (pytest)
   │
   ├─→ build-and-push (Docker build → ECR push)
   │
   └─→ deploy         (ECS force-new-deployment, rolling update)
```

Rolling update stratejisi (`minimum_healthy_percent = 100`) sayesinde deployment sıfır kesintili gerçekleşir.

---

## Katman 4: Otomatik Ölçeklendirme Katmanı

Bu katman sistemin "otomatik pilot" özelliğinin kalbidir (bkz. [autoscaling.md](autoscaling.md)).

**Kapalı döngü (closed loop):**

```
EventBridge (her 2 dk)
   │
   ▼
Lambda (autoscaler)
   │
   ├─→ CloudWatch'tan son 5 dk CPU metriklerini oku
   ├─→ Ortalama CPU'yu hesapla (moving average)
   ├─→ Eşik-tabanlı karar ver (SCALE_UP / SCALE_DOWN / NO_CHANGE)
   ├─→ Karar SCALE ise → ECS desired_count güncelle (MIN=1, MAX=4 sınırlı)
   └─→ Kararı CloudWatch Logs'a yaz (audit trail)
```

**Neden Lambda + EventBridge:** Autoscaler mantığı sürekli çalışan bir sunucu gerektirmez. EventBridge'in periyodik tetiklemesi hem yeterli sıklık hem de doğal bir cooldown (2 dk aralık) sağlar. Sistem tamamen sunucusuz ve otonom çalışır.

---

## Katman 5: Gözlemlenebilirlik & Maliyet Katmanı

(Bkz. [monitoring-and-cost.md](monitoring-and-cost.md))

- **CloudWatch Metrics** — ECS ve ALB metrikleri otomatik toplanır
- **CloudWatch Alarms** — CPU %85'i aşınca tetiklenir
- **SNS** — alarm tetiklendiğinde (ve normale döndüğünde) email bildirimi
- **CloudWatch Logs** — Lambda'nın her kararı denetlenebilir şekilde loglanır
- **Cost Explorer entegrasyonu** — servis bazlı maliyet raporu + idle kaynak tespiti

---

## Veri Akışı Özeti

```
                    ┌─────────────┐
   Kullanıcı/Yük ──→│     ALB     │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐      ┌──────────────┐
                    │ ECS Fargate │─────→│  CloudWatch  │
                    │  (FastAPI)  │      │   Metrics    │
                    └─────────────┘      └──────┬───────┘
                           ▲                    │
                           │                    ▼
                    ┌──────┴───────┐     ┌──────────────┐
                    │ desired_count│←────│    Lambda    │←── EventBridge (2dk)
                    │   güncelle   │     │ (autoscaler) │
                    └──────────────┘     └──────┬───────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │ CloudWatch   │
                                         │ Logs (audit) │
                                         └──────────────┘
```

---

## İlgili Kararlar

Bu mimarideki temel tercihler ADR'larda gerekçelendirilmiştir:
- [Neden Terraform](adr/0001-neden-terraform.md)
- [Neden Fargate](adr/0003-neden-fargate.md)
- [Neden Lambda'ya taşındı](adr/0008-lambda-tasima.md)

[← Ana sayfaya dön](../README.md)
