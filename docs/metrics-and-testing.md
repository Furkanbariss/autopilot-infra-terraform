# Metrics & Testing — Ölçümler, Testler ve Kısıtlamalar

[← Ana sayfaya dön](../README.md)

Bu doküman, README'deki metriklerin **nasıl ölçüldüğünü** şeffaf şekilde açıklar ve sistemin bilinen sınırlarını dürüstçe raporlar. Tüm sayılar gerçek ölçümlere dayanır.

---

## Test Ortamı

- Tek servis, tek bölge (`eu-north-1`)
- Yük, özel bir load generator ile üretilmiştir (gerçek kullanıcı trafiği değil)
- Fazlı yük senaryoları: düşük / orta / yüksek (burst) / cooldown

Bu bir **kontrollü test ortamıdır** — üretim ölçeğinde milyonlarca istek değil, mühendislik prensiplerinin doğrulandığı bir kanıt (proof-of-concept) ortamıdır.

---

## Ölçülen Metrikler

### 1. Altyapı Kurulum Süresi (RTO) — ~3.5 dakika

**Ölçüm yöntemi:**
```powershell
terraform destroy
Measure-Command { terraform apply -auto-approve }
```
**Sonuç:** 3 dakika 29 saniye — tüm ortamın (VPC, ALB, ECS, ECR, IAM, Lambda, SNS) sıfırdan kurulumu.

**Anlamı:** Bir felaket senaryosunda tüm altyapı ~3.5 dakikada yeniden kurulabilir (Recovery Time Objective).

---

### 2. CI/CD Deploy Süresi — ~1 dakika

**Ölçüm yöntemi:** GitHub Actions workflow "Total duration" değeri.

**Sonuç:** 1 dakika 12 saniye (test + build-and-push ~43s + deploy ~8s).

---

### 3. Ölçeklendirme Tepki Süresi — ~57 saniye

**Ölçüm yöntemi:** İki timestamp'in farkı:
- Lambda'nın `SCALE_UP` kararı verdiği an (CloudWatch Logs): `13:22:34`
- Yeni ECS task'ının "Running" durumuna geçtiği an (ECS task detayı): ~`13:23:31`

**Sonuç:** ~57 saniye (karardan yeni kapasitenin ayağa kalkmasına kadar).

**Bonus gözlem:** Docker image'ının ECR'dan çekilmesi (`Pull completed`) yalnızca **3 saniye** sürmüştür — image'ın verimli boyutta olduğunu gösterir.

---

### 4. Deployment Kesinti — 0 başarısız istek

**Ölçüm yöntemi:** Load generator, deploy sırasında sürekli istek gönderirken, her isteğin sonucu (başarılı/başarısız) timestamp'li olarak loglanmıştır.

**Sonuç:** Deploy penceresi boyunca (16:56–16:58) gönderilen tüm istekler `status=200`, **0 başarısız istek** (`hatali=0`).

**Kanıt:** [`deploy-probe.log`](../deploy-probe.log) — timestamp'li tam istek logu.

Bu, rolling update (`minimum_healthy_percent = 100`) sayesinde sıfır kesintili deployment'ın kanıtıdır.

---

## Bilinen Kısıtlama: Provisioning Lag

**Gözlem:** Aşırı ve ani yük artışlarında (5x paralel istek, istek başına 500.000 iterations), load generator zaman aşımı (`Read timed out`) hataları almaya başlamıştır.

**Sebep:** Bu hatalar **deployment kaynaklı değildir** — reaktif (metrik-tabanlı) autoscaling'in doğal bir sınırıdır. Yük artış hızı, autoscaler'ın yeni task ekleme hızını (karar + task başlatma ~57sn) geçtiğinde, mevcut task'lar geçici olarak boğulur ve timeout oluşur. Buna **provisioning lag** denir.

**Bu neden gizlenmiyor:** Her sistemin bir kapasite sınırı vardır. Önemli olan sınırı bilmek ve ona göre önlem alabilmektir. Bu kısıtlama, sistemin gerçekten stres testine tabi tutulduğunun ve sınırlarının anlaşıldığının göstergesidir.

**Olası İyileştirmeler:**
| Yaklaşım | Etki |
|----------|------|
| Scale-up eşiğini düşürmek (70 → 50) | Daha erken tepki |
| Bir seferde birden fazla task eklemek (+1 → +2) | Ani yüke daha hızlı kapasite |
| Baseline task sayısını artırmak (1 → 2) | Ani spike'lara hazır bekleyen kapasite |
| Predictive scaling | Yükü önceden tahmin edip proaktif ölçeklendirme |

Son madde, projenin erken aşamasında değerlendirilen ML-tabanlı tahmin yaklaşımıyla örtüşür — reaktif değil proaktif bir çözüm olarak gelecekteki bir yön olabilir.

---

## Test Senaryoları Özeti

| Test | Amaç | Sonuç |
|------|------|-------|
| Sıfırdan kurulum | RTO ölçümü | ~3.5 dk |
| CI/CD tetikleme | Deploy süresi | ~1 dk |
| Fazlı yük + autoscaling | Tepki süresi | ~57 sn |
| Deploy sırasında yük | Kesinti ölçümü | 0 hata |
| Aşırı burst yükü | Sınır testi | Provisioning lag tespit edildi |

---

[← Ana sayfaya dön](../README.md)
