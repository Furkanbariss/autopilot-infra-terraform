# ADR-0007: Rolling Update Deployment Stratejisi

## Durum
Kabul edildi

## Bağlam
Yeni versiyonlar deploy edilirken kesinti (downtime) yaşanmaması hedeflendi.

## Değerlendirilen Seçenekler
1. **Blue-Green (CodeDeploy ile)** — iki ayrı ortam, anlık trafik geçişi, otomatik rollback; güçlü ama karmaşık
2. **Rolling Update (ECS yerleşik)** — kademeli task değişimi, `minimum_healthy_percent` kontrolü

## Karar
Rolling update tercih edildi.

## Gerekçe
- **Yeterlilik:** `minimum_healthy_percent = 100` ayarı sayesinde, yeni task sağlıklı olmadan eski task durdurulmuyor — pratikte sıfır kesinti sağlanıyor
- **Basitlik:** CodeDeploy'un ek karmaşıklığı (ayrı target group, deployment group, IAM) olmadan hedefe ulaşıyor
- **Uygun ölçek:** Bu proje ölçeğinde blue-green'in ek izolasyonu gereksiz

## Sonuçlar
- Deploy sırasında sürekli trafik altında **0 başarısız istek** ölçüldü (kanıt: deploy-probe.log)
- Blue-green, daha yüksek izolasyon gerektiren gelecekteki bir senaryo için değerlendirilebilir
