output "security_group_id" {
  description = "Olusturulan security group ID"
  value       = aws_security_group.web_sg.id
}

output "alb_dns_name" {
  value = aws_lb.app.dns_name
}

output "rds_endpoint" {
  description = "RDS baglanti adresi"
  value       = aws_db_instance.main.endpoint
}

output "db_secret_arn" {
  description = "Veritabani kimlik bilgilerinin Secrets Manager ARN'i"
  value       = aws_secretsmanager_secret.db_credentials.arn
}
