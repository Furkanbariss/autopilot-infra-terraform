variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "kaynak isimlendirmede kullanmak için projenin adı"
  type        = string
  default     = "furkan-autopilot"
}

# variable "api_key_example" {
#   description = "AWS secret manager'da kullanılmak üzere oluşturduğum örnek KEY'ler"
#   type = map(string) # hepsine sıra sıra uygulanması için map fonksiyonunu kullandık
#   default = {
#     API_KEY     = "example-willChange-api-key"
#     DB_PASSWORD = "example-willChange-password"
#   }
# }
