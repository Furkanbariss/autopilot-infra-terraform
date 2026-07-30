# ADR-0005: Kural-Tabanlı Ölçeklendirme (ML Değil)

## Durum
Kabul edildi

## Bağlam
Otomatik ölçeklendirme kararı için bir mantık gerekiyordu. Projenin erken aşamasında makine öğrenmesi tabanlı bir CPU tahmin modeli (Random Forest/LSTM) değerlendirildi ve prototiplendi.

## Değerlendirilen Seçenekler
1. **ML-tabanlı tahmin** — proaktif ama karmaşık, "kara kutu", açıklanması zor
2. **Kural-tabanlı (threshold + moving average)** — reaktif ama açıklanabilir, öngörülebilir

## Karar
Kural-tabanlı yaklaşım seçildi.

## Gerekçe
- **Açıklanabilirlik:** Her karar tam olarak izlenebilir ve gerekçelendirilebilir
- **Öngörülebilirlik:** Üretim ortamında davranış tahmin edilebilir
- **Denetlenebilirlik:** ML modelinin "kara kutu" doğası yerine, her kararın nedeni loglanabilir
- **Sürdürülebilirlik:** Karar mantığının her satırı anlaşılabilir ve savunulabilir

## Sonuçlar
- Moving average + eşik + cooldown kombinasyonu gürültü ve salınım sorunlarını çözüyor
- Her karar, insan-okunabilir bir gerekçeyle loglanıyor
- ML-tabanlı proaktif yaklaşım, gelecekteki bir iyileştirme olarak kapı açık bırakıldı (bkz. provisioning lag kısıtlaması)
