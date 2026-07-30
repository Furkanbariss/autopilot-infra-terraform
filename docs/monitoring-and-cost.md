# Monitoring & Cost — Gözlemlenebilirlik ve Maliyet

[← Ana sayfaya dön](../README.md)

Sistem, kendini izleyen ve maliyetini raporlayan bir gözlemlenebilirlik katmanına sahiptir.

---

## CloudWatch Metrics

ECS ve ALB, aşağıdaki metrikleri otomatik olarak CloudWatch'a gönderir:

| Metrik | Kaynak | Kullanım |
|--------|--------|----------|
| `CPUUtilization` | ECS | Autoscaling karar girdisi |
| `MemoryUtilization` | ECS | İzleme |
| `RequestCount` | ALB | Trafik analizi |
| `TargetResponseTime` | ALB | Gecikme izleme |

---

## CloudWatch Alarms + SNS

Kritik durumlar için otomatik uyarı mekanizması kurulmuştur.

### Yüksek CPU Alarmı
```hcl
threshold           = 85       # %85 eşiği
evaluation_periods  = 2        # 2 ardışık periyot
period              = 60       # 60 saniyelik periyotlar
```

**Neden 2 evaluation period:** Tek anlık spike'ta alarm çalmasın diye — "2 ardışık periyot boyunca eşiği aşarsa" mantığı, gürültüye karşı koruma sağlar (autoscaler'daki moving average mantığının alarm karşılığı).

### SNS Bildirimi
- Alarm tetiklendiğinde (`alarm_actions`) → email bildirimi
- Sistem normale döndüğünde (`ok_actions`) → "düzeldi" bildirimi

Bu çift yönlü bildirim, durumun başından sonuna takip edilmesini sağlar.

---

## Audit Logging

İki seviyede loglama vardır:

1. **Container logları** → CloudWatch Log Group (`/ecs/furkan-autopilot-task`, 7 gün retention)
2. **Autoscaler kararları** → Lambda'nın CloudWatch Logs'u (her karar, gerekçesiyle)

---

## Maliyet Yönetimi (FinOps)

### Servis Bazlı Maliyet Raporu
AWS Cost Explorer API üzerinden son 7 günün maliyeti, servis bazında çekilir ve raporlanır.

> **Not:** Cost Explorer API yalnızca `us-east-1` bölgesinde çalışır (altyapı `eu-north-1`'de olsa bile). Bu, sık karşılaşılan bir tuzaktır ve kodda dikkate alınmıştır.

### Idle Kaynak Tespiti
Boşta duran ama ücret alan kaynaklar otomatik tespit edilir:
- Bağlı olmayan EBS volume'ler (`available` durumunda)
- Hiçbir kaynağa bağlı olmayan Elastic IP'ler
- Durdurulmuş ama silinmemiş EC2 instance'lar

Bu üç kaynak, gerçek dünyada en yaygın "sessiz para yakan" kaynaklardır.

### Haftalık Rapor
Bot, markdown formatında bir maliyet raporu üretir (servis bazlı maliyet + optimizasyon önerileri).

**Otomatikleştirme (gelecek iyileştirme):** Rapor botu, autoscaler ile aynı yöntemle (Lambda + EventBridge cron) haftalık otomatik tetiklenebilir ve SNS ile email olarak gönderilebilir.

---

## İlgili Kararlar
- [ADR-0009: Maliyet optimizasyon stratejisi](adr/0009-maliyet-stratejisi.md)

[← Ana sayfaya dön](../README.md)
