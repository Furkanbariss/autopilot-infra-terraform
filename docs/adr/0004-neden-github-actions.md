# ADR-0004: CI/CD için GitHub Actions

## Durum
Kabul edildi

## Bağlam
Kod değişikliklerinin otomatik test edilip dağıtılması için bir CI/CD aracı gerekli.

## Değerlendirilen Seçenekler
1. **GitHub Actions** — repo zaten GitHub'da, entegre
2. **AWS CodePipeline** — AWS-native ama ek servis kurulumu ve entegrasyon gerektirir
3. **Jenkins** — güçlü ama ayrı sunucu kurulumu ve bakımı gerektirir

## Karar
GitHub Actions seçildi.

## Gerekçe
- **Entegrasyon:** Kod zaten GitHub'da — ek servis entegrasyonu gerekmez
- **Basitlik:** YAML tabanlı, öğrenme eğrisi düşük
- **Bakım yok:** Jenkins gibi ayrı bir sunucu yönetilmez
- **Ücretsiz:** Public/kişisel projeler için yeterli ücretsiz kota

## İlgili Yaml dosyası
> Detaylı yaml dosyası için → **[autopilot-app-CI/CD-yaml](https://github.com/Furkanbariss/autopilot-app/blob/main/.github/workflows/deploy.yml)**

## Sonuçlar
- Push → test → build → ECR push → ECS deploy pipeline'ı otomatik çalışıyor
- Test başarısız olursa deploy hiç çalışmıyor (hatalı kod canlıya çıkmıyor)
- Pipeline süresi ~1 dakika

