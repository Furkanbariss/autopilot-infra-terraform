output "instance_public_ip" {
  description = "Web sunucusunun public IP adresi"
  value       = aws_instance.web_server.public_ip
}

output "security_group_id" {
  description = "Olusturulan security group ID"
  value       = aws_security_group.web_sg.id
}

output "server_name" {
  value = aws_instance.web_server.tags["Name"]
}