variable "project_name" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  type    = string
  default = "10.0.2.0/24"
}

variable "availability_zone" {
  type    = string
  default = "eu-north-1a"
}

variable "public_subnet_cidr_2" {
  type    = string
  default = "10.0.3.0/24"
}

variable "availability_zone_2" {
  type    = string
  default = "eu-north-1b" 
}