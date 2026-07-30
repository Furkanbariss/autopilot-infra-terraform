# Architecture Decision Records (ADR)

[← Ana sayfaya dön](../../README.md)

Bu klasör, projedeki önemli mimari kararların gerekçelerini içerir. Her ADR; kararın bağlamını, değerlendirilen seçenekleri, verilen kararı ve sonuçlarını belgeler.

**ADR neden tutulur:** 6 ay sonra "neden bu teknolojiyi/yaklaşımı seçmişim" sorusunun cevabı yazılı kalsın diye. Bu, "tutorial takip etmedim, bilinçli karar verdim" mesajının kanıtıdır.

---

## ADR Listesi

| No | Karar | Durum |
|----|-------|-------|
| [0001](0001-neden-terraform.md) | Infrastructure as Code için Terraform | Kabul edildi |
| [0002](0002-neden-remote-state.md) | S3 remote state kullanımı | Kabul edildi |
| [0003](0003-neden-fargate.md) | Compute için ECS Fargate | Kabul edildi |
| [0004](0004-neden-github-actions.md) | CI/CD için GitHub Actions | Kabul edildi |
| [0005](0005-neden-kural-tabanli.md) | Kural-tabanlı ölçeklendirme (ML değil) | Kabul edildi |
| [0006](0006-min-max-task-siniri.md) | MIN/MAX task sınırı | Kabul edildi |
| [0007](0007-rolling-update.md) | Rolling update deployment stratejisi | Kabul edildi |
| [0008](0008-lambda-tasima.md) | Autoscaler'ın Lambda'ya taşınması | Kabul edildi |
| [0009](0009-maliyet-stratejisi.md) | Maliyet optimizasyon stratejisi | Kabul edildi |
| [0010](0010-iki-repo-ayrimi.md) | Uygulama ve altyapı ayrı repolarda | Kabul edildi |

[← Ana sayfaya dön](../../README.md)
