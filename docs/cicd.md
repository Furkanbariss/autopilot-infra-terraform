# CI/CD — GitHub Actions Pipeline

[← Ana sayfaya dön](../README.md)

Her kod değişikliği, GitHub Actions üzerinden otomatik olarak test edilir, paketlenir ve dağıtılır.

---

## Pipeline Akışı

`main` branch'ine her push, üç aşamalı bir pipeline'ı tetikler:

```
git push (main)
   │
   ├─→ [test]            pytest ile otomatik test
   │        │
   │        ▼ (başarılıysa)
   ├─→ [build-and-push]  Docker build → ECR'a image push
   │        │
   │        ▼ (başarılıysa)
   └─→ [deploy]          ECS force-new-deployment (rolling update)
```

Her aşama bir öncekinin başarılı olmasına bağlıdır (`needs`). Test başarısız olursa, build ve deploy hiç çalışmaz — **hatalı kod asla canlıya çıkmaz.**

**Ölçülen pipeline süresi:** ~1 dakika 12 saniye (test + build-and-push ~43s + deploy ~8s).

---

## Güvenlik: Credentials Yönetimi

AWS erişim bilgileri asla kodda tutulmaz. GitHub Secrets üzerinden güvenli şekilde sağlanır:

| Secret | Amaç |
|--------|------|
| `AWS_ACCESS_KEY_ID` | AWS kimlik |
| `AWS_SECRET_ACCESS_KEY` | AWS gizli anahtar |
| `AWS_REGION` | Bölge (`eu-north-1`) |
| `ECR_REPOSITORY` | Hedef ECR repo adı |

---

## Image Etiketleme Stratejisi

Her image iki tag ile push edilir:
- `${github.sha}` — commit hash'i (hangi kodun hangi image'a karşılık geldiğinin izlenebilirliği)
- `latest` — ECS Task Definition'ın referans aldığı tag

Bu, "hangi commit şu an canlıda" sorusunun cevabını izlenebilir kılar.

---

## Zero-Downtime Deployment

Deploy aşaması, ECS'in **rolling update** özelliğini kullanır. ECS Service'te:

```hcl
deployment_minimum_healthy_percent = 100
deployment_maximum_percent         = 200
```

**Nasıl çalışır:**
- `minimum_healthy_percent = 100` → deploy sırasında her zaman en az %100 kapasite (mevcut task'lar) ayakta kalır
- `maximum_percent = 200` → geçici olarak eski + yeni task'lar birlikte çalışabilir
- Yeni task health check'ten geçmeden eski task durdurulmaz

**Sonuç:** Deploy sırasında sistem kesintisiz erişilebilir kalır. (Ölçüm: deploy sırasında sürekli trafik altında 0 başarısız istek — kanıt: [`deploy-probe.log`](../deploy-probe.log), detay: [metrics-and-testing.md](metrics-and-testing.md))

Blue-green deployment de değerlendirilmiş, bu ölçek için rolling update'in yeterli olduğu sonucuna varılmıştır. (bkz. [ADR-0007](adr/0007-rolling-update.md))

---

## Örnek Workflow (özet)

```yaml
name: Build, Test, and Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
      - uses: aws-actions/amazon-ecr-login@v2
      - run: docker build & push (sha + latest)

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - run: aws ecs update-service --force-new-deployment
```

---

## İlgili Kararlar
- [ADR-0004: Neden GitHub Actions](adr/0004-neden-github-actions.md)
- [ADR-0007: Rolling update stratejisi](adr/0007-rolling-update.md)

[← Ana sayfaya dön](../README.md)
