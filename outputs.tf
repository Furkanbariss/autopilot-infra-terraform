output "security_group_id" {
  description = "Olusturulan security group ID"
  value       = aws_security_group.web_sg.id
}

output "alb_dns_name" {
  value = aws_lb.app.dns_name
}
