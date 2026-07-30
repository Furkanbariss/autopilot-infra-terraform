# Infrastructure — Terraform / IaC

[← Ana sayfaya dön](../README.md)

Tüm altyapı Terraform ile kod olarak tanımlıdır. Bu, ortamın tekrarlanabilir, versiyonlanabilir ve tek komutla kurulabilir olmasını sağlar.

---

## Kod Yapısı

```
autopilot-infra-terraform/
├── main.tf                    # Ana kaynaklar (ECS, ALB, ECR, IAM, Lambda, SNS...)
├── variables.tf               # Değişkenler (region, project_name)
├── outputs.tf                 # Çıktılar (ALB DNS, ECR URL...)
├── modules/
│   └── networking/            # VPC modülü
│       ├── main.tf            # VPC, subnet, IGW, route table
│       ├── variables.tf
│       └── outputs.tf
```

---

## Remote State

State dosyası, güvenli ve tutarlı yönetim için S3'te saklanır:

```hcl
backend "s3" {
  bucket = "furkan-terraform-state-2121"
  key    = "autopilot-infra/terraform.tfstate"
  region = "eu-north-1"
}
```

**Neden remote state:** Local state dosyası kaybolabilir, ekip çalışmasında çakışabilir. S3 backend, state'i merkezi ve versiyonlanmış tutar. (bkz. [ADR-0002](adr/0002-neden-remote-state.md))

---

## Networking Modülü

Ağ kaynakları ayrı bir modülde toplanmıştır (`modules/networking`):

| Kaynak | Amaç |
|--------|------|
| `aws_vpc` | İzole ağ (`10.0.0.0/16`) |
| `aws_subnet` (public x2) | ALB ve Fargate için, 2 farklı AZ'de |
| `aws_internet_gateway` | Dış internet erişimi |
| `aws_route_table` + association | Public subnet trafik yönlendirmesi |

**Modüler yapının faydası:** Ağ kaynakları tek bir yerde toplanır, ana kod sadeleşir, gerektiğinde yeniden kullanılabilir.

---

## Compute & Container Kaynakları

| Kaynak | Açıklama |
|--------|----------|
| `aws_ecr_repository` | Docker image deposu (`force_delete` ile temiz destroy) |
| `aws_ecs_cluster` | Fargate cluster |
| `aws_ecs_task_definition` | Container tanımı (256 CPU / 512 MB, port 8000) |
| `aws_ecs_service` | Rolling update stratejili service |
| `aws_iam_role` (task execution) | ECS'in ECR pull + CloudWatch log yazma yetkisi |
| `aws_cloudwatch_log_group` | Container logları (7 gün retention) |

---

## Load Balancing

| Kaynak | Açıklama |
|--------|----------|
| `aws_lb` | Application Load Balancer (internet-facing) |
| `aws_lb_target_group` | IP-tabanlı hedef grubu, `/health` health check |
| `aws_lb_listener` | Port 80 → target group forward |

**Not:** ALB, en az 2 farklı Availability Zone'da subnet gerektirir — bu yüzden networking modülünde iki public subnet tanımlanmıştır.

---

## Tek Komutla Kurulum ve Yıkım

```bash
terraform init      # backend + provider hazırlığı
terraform plan      # değişiklik önizlemesi
terraform apply     # tüm altyapıyı kur (~3.5 dakika)
terraform destroy   # tüm altyapıyı temizle
```

**Ölçülen kurulum süresi:** `terraform destroy` sonrası `terraform apply` ile tüm ortam **~3 dakika 29 saniye**de sıfırdan kuruldu (`Measure-Command` ile ölçüldü). Bu, sistemin RTO'su (Recovery Time Objective) olarak değerlendirilebilir.

---

## Uygulama Image'ini Deploy Etme (İlk Kurulum)

Terraform ECR repository'yi oluşturur ama image'ı içine koymaz. İlk kurulumda:

```bash
# ECR'a login
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-north-1.amazonaws.com

# Build, tag, push
docker build -t furkan-autopilot-fastapi-app .
docker tag furkan-autopilot-fastapi-app:latest <account-id>.dkr.ecr.eu-north-1.amazonaws.com/furkan-autopilot-fastapi-app:latest
docker push <account-id>.dkr.ecr.eu-north-1.amazonaws.com/furkan-autopilot-fastapi-app:latest
```

Sonraki deploy'lar CI/CD pipeline'ı üzerinden otomatik yapılır (bkz. [cicd.md](cicd.md)).

---

## İlgili Kararlar
- [ADR-0001: Neden Terraform](adr/0001-neden-terraform.md)
- [ADR-0002: Neden remote state](adr/0002-neden-remote-state.md)
- [ADR-0003: Neden Fargate](adr/0003-neden-fargate.md)

[← Ana sayfaya dön](../README.md)
