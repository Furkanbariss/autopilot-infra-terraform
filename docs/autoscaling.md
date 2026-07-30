# Autoscaling — Otomatik Ölçeklendirme Motoru

[← Ana sayfaya dön](../README.md)

Sistemin "otomatik pilot" özelliğinin kalbi. CloudWatch metriklerini analiz eden, kural-tabanlı bir karar motoru; sunucusuz (Lambda) ve otonom (EventBridge) çalışır.

---

## Neden Kural-Tabanlı (ML Değil)?

Karar mantığı için makine öğrenmesi tabanlı tahmin yerine **eşik-tabanlı (threshold) bir yaklaşım** seçilmiştir. Gerekçe:

- **Açıklanabilirlik:** Her karar tam olarak izlenebilir ve gerekçelendirilebilir
- **Öngörülebilirlik:** Üretim ortamında davranış tahmin edilebilir
- **Denetlenebilirlik:** "Kara kutu" bir model yerine, her kararın nedeni loglanabilir

(bkz. [ADR-0005](adr/0005-neden-kural-tabanli.md))

---

## Karar Mantığı

Karar motoru üç mekanizmayı birleştirir:

### 1. Moving Average (Hareketli Ortalama)
Son 5 ölçümün ortalaması alınır. Bu, tek seferlik CPU sıçramalarının (spike) gereksiz ölçeklendirmeye yol açmasını engeller — anlık gürültüyü filtreler.

### 2. Eşik Karşılaştırması
```
ortalama_cpu > 70  →  SCALE_UP
ortalama_cpu < 20  →  SCALE_DOWN
aksi halde         →  NO_CHANGE
```

### 3. Güvenlik Sınırları (MIN/MAX)
```
MIN_TASKS = 1   (asla 0'a düşme)
MAX_TASKS = 4   (asla 4'ün üstüne çıkma — maliyet koruması)
```

**Neden MAX sınırı kritik:** Bir bug ya da anormal metrik "sürekli scale up" kararı ürettiğinde, sınır olmadan sistem onlarca task açıp maliyeti patlatabilir. Bu tek sınır, maliyet bilincinin somut kanıtıdır. (bkz. [ADR-0006](adr/0006-min-max-task-siniri.md))

---

## Lambda'ya Taşıma

Autoscaler başlangıçta local'de bir Python scripti olarak geliştirilip test edildi. Doğrulandıktan sonra, üretim için AWS Lambda'ya taşındı.

**Neden taşındı:** Sürekli çalışan bir sunucu (ya da geliştiricinin laptop'u) gerektirmemesi için. Sistem, hiçbir yerel bağımlılık olmadan, tamamen cloud'da otonom çalışmalıdır.

**Mimari dönüşüm:**
| Local versiyon | Lambda versiyonu |
|----------------|------------------|
| `while True` sonsuz döngü | Tek seferlik `lambda_handler`, EventBridge tekrarlar |
| CSV dosyasına audit log | `print()` → CloudWatch Logs (otomatik) |
| State'li cooldown | Stateless (EventBridge aralığı doğal cooldown) |

(bkz. [ADR-0008](adr/0008-lambda-tasima.md))

---

## EventBridge ile Zamanlama

Lambda, EventBridge kuralı ile her 2 dakikada bir tetiklenir:

```hcl
schedule_expression = "rate(2 minutes)"
```

Bu aralık, hem yeterince sık (yüke hızlı tepki) hem de yeterince seyrek (salınımı önleyen doğal cooldown) olacak şekilde seçilmiştir.

---

## IAM Least-Privilege

Lambda'ya yalnızca ihtiyaç duyduğu izinler verilmiştir:

```
cloudwatch:GetMetricStatistics   → metrik okuma
ecs:DescribeServices             → service durumu okuma
ecs:UpdateService                → SADECE tek bir ECS service'i güncelleme
```

**Kritik detay:** `ecs:UpdateService` izni, `Resource` alanıyla **tek bir service'e** kısıtlanmıştır. Yani Lambda, başka hiçbir ECS service'ini değiştiremez — gerçek least-privilege. (bkz. [ADR-0008](adr/0008-lambda-tasima.md))

---

## Audit Trail

Her karar döngüsü CloudWatch Logs'a yazılır:

```json
{
  "timestamp": "2026-07-30T13:22:34+00:00",
  "avg_cpu": 71.22,
  "action": "SCALE_UP",
  "reason": "Ortalama CPU 71.2 > 70",
  "count_before": 2,
  "count_after": 3
}
```

`reason` alanı, her kararın **insan-okunabilir gerekçesini** içerir — bu, sistemin neden o kararı verdiğini geriye dönük analiz etmeyi mümkün kılar.

---

## Gerçek Çalışma Kanıtı

CloudWatch Logs'tan gözlemlenen gerçek ölçeklendirme dizisi:

```
13:20:34  SCALE_UP    CPU 70.09  →  1 → 2 task
13:22:34  SCALE_UP    CPU 71.22  →  2 → 3 task
13:24:34  NO_CHANGE   CPU 69.34  →  3 task (normal aralık)
13:26:34  NO_CHANGE   CPU 46.03  →  3 task
```

**Ölçülen tepki süresi:** İlk SCALE_UP kararından (13:22:34) yeni task'ın "Running" olmasına kadar **~57 saniye**.

---

## İlgili Kararlar
- [ADR-0005: Neden kural-tabanlı karar](adr/0005-neden-kural-tabanli.md)
- [ADR-0006: MIN/MAX task sınırı](adr/0006-min-max-task-siniri.md)
- [ADR-0008: Lambda'ya taşıma ve stateless mimari](adr/0008-lambda-tasima.md)

[← Ana sayfaya dön](../README.md)
