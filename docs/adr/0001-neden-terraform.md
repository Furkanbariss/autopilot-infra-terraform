# ADR-0001: Infrastructure as Code için Terraform

## Durum
Kabul edildi

## Bağlam
Altyapı (VPC, ECS, ALB, IAM vb.) elle (AWS Console'dan tıklayarak) da kurulabilirdi. Ancak elle kurulum tekrarlanabilir değildir, unutulur, hataya açıktır ve versiyon kontrolü yapılamaz.

## Değerlendirilen Seçenekler
1. **Elle (Console) kurulum** — hızlı başlangıç ama tekrarlanamaz, sürdürülemez
2. **AWS CloudFormation** — AWS-native ama yalnızca AWS'ye bağlı
3. **Terraform** — çoklu-cloud destekli, en yaygın IaC aracı, geniş topluluk

## Karar
Terraform seçildi.

## Gerekçe
- **Tekrarlanabilirlik:** Aynı kod, aynı altyapıyı istenildiği kadar kurabilir
- **Versiyon kontrolü:** Altyapı değişiklikleri Git ile takip edilebilir
- **Çoklu-cloud:** CloudFormation'ın aksine tek platforma bağlı değil (CV'de daha değerli bir beceri)
- **Ekosistem:** En yaygın IaC aracı, dokümantasyon ve topluluk desteği güçlü

## Sonuçlar
- Tüm altyapı tek komutla (`terraform apply`) ~3.5 dakikada kurulabiliyor
- `terraform destroy` ile temiz şekilde kaldırılabiliyor (maliyet kontrolü)
- Kod, altyapının en güncel dokümantasyonu işlevi görüyor
