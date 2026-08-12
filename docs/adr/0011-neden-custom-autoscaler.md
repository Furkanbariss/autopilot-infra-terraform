# ADR-0011: Custom Lambda Autoscaler vs. AWS Native ECS Application Auto Scaling

## Durum
Kabul edildi

## Bağlam
AWS'nin ECS için yerleşik bir otomatik ölçeklendirme servisi vardır: **Application Auto Scaling** (Target Tracking Scaling Policy). Bu servis, CloudWatch metriklerine (örn. CPUUtilization) göre `desired_count`'u otomatik olarak ayarlar — tam olarak bu projedeki custom Lambda autoscaler'ın yaptığı işin native karşılığı.

Bu ADR, mentor code review sürecinde gelen bir geri bildirim üzerine yazılmıştır: native servis dururken neden ayrı bir Lambda tabanlı çözüm inşa edildiği netleştirilmelidir.

## Değerlendirilen Seçenekler
1. **AWS Application Auto Scaling (native)** — hazır, yönetilen, sıfır bakım gerektiren target tracking servisi
2. **Custom Lambda + EventBridge autoscaler (bu projede uygulanan)** — moving average, trend detection ve özel cooldown mantığı içeren, sıfırdan yazılmış karar motoru

## Karar
Bu proje kapsamında bilinçli olarak custom Lambda tabanlı bir autoscaler geliştirildi.

## Gerekçe
- **Öğrenme amacı:** Bu projenin birincil hedefi, autoscaling'in native serviste "kara kutu" olarak sunulan iç mantığını (metrik toplama, gürültü filtreleme, karar üretimi, kaynak güncelleme) baştan sona inşa ederek anlamaktı.
- **Native serviste bulunmayan esneklik:** Target Tracking Scaling, tek bir metrik + hedef değer üzerinden çalışır. Bu projede denenen moving average (ani spike filtreleme) ve basit trend detection (yükseliş/düşüş yönü) gibi mekanizmalar, native serviste doğrudan yapılandırılamaz.
- **Denetlenebilirlik:** Custom çözüm, her kararı insan-okunabilir bir gerekçeyle (`reason` alanı) loglar. Native serviste bu seviyede özelleştirilmiş audit trail yoktur.

## Production İçin Dürüst Değerlendirme
Gerçek bir production ortamında, **ilk tercih AWS Application Auto Scaling olurdu.** Gerekçesi:
- Sıfır bakım, AWS tarafından yönetilir ve test edilir
- Daha az kod = daha az hata yüzeyi
- Custom bir çözüm yalnızca native servisin karşılamadığı çok özel bir iş mantığı olduğunda gerekçelendirilir (örn. birden fazla metriğin özel bir formülle birleştirilmesi, iş-saatine göre farklı davranış, harici bir sistemden gelen sinyalle ölçeklendirme)

Bu proje, bu gerçek gerekçelerden ziyade **öğrenme amacıyla** custom yola gitmiştir ve bu, bilinçli bir trade-off olarak burada belgelenmiştir.

## Sonuçlar
- Custom autoscaler, projenin CloudWatch → Lambda → ECS → audit log döngüsünü uçtan uca göstermesi amacıyla korunmuştur
- README ve ilgili dokümantasyona, bu kararın native alternatifle karşılaştırmalı gerekçesi eklenmiştir
- Gelecekte production-benzeri bir senaryo simüle edilmek istenirse, native Application Auto Scaling ile bir karşılaştırma (A/B) denemesi yapılabilir
