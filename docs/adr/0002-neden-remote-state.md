# ADR-0002: S3 Remote State Kullanımı

## Durum
Kabul edildi

## Bağlam
Terraform, oluşturduğu kaynakların durumunu bir state dosyasında (`terraform.tfstate`) takip eder. Bu dosya varsayılan olarak local makinede tutulur.

## Değerlendirilen Seçenekler
1. **Local state** — basit ama kaybolabilir, ekip çalışmasında çakışır, güvensiz
2. **S3 remote state** — merkezi, versiyonlanabilir, güvenli

## Karar
S3 backend ile remote state kullanıldı.

## Gerekçe
- **Güvenlik:** State dosyası local'de kaybolursa Terraform mevcut altyapıyı "unutur" — bu felakettir
- **Versiyonlama:** S3 bucket versioning ile state'in geçmiş sürümlerine dönülebilir
- **Profesyonel pratik:** Gerçek ekip ortamlarında standart yaklaşım budur

## Sonuçlar
- State, `furkan-terraform-state-2121` S3 bucket'ında saklanıyor
- Bucket versioning aktif — kazara bozulmalara karşı koruma
- Local state'in riskleri ortadan kalktı
