terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-web-sg-tf"
  description = "SSH ve HTTP erisimi icin"
  vpc_id = module.networking.vpc_id

  ingress { # (in gress) içeri giriş portları
    description = "SSH"
    from_port   = 22 #22. porttan başla
    to_port     = 22 #22. porta kadar girişe izin ver
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Not: Gerçek projelerde kendi IP'ni vermen gerek. Burası erişebilecek IP'leri temsil eder. 0.0.0.0/0 ise tüm IP'lere açık olduğu anlamına gelir.
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress { # (Exit GRESS) dışarı çıkış portları 
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # tüm protokolere açık demek
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-web-sg-tf"
  }
}

resource "aws_s3_bucket" "terraform_test_bucket" {
  bucket = "furkan-terraform-unique-test-bucket-2204"
}

data "aws_key_pair" "existing_key" { #data ile daha önceden bende var olan keyi çekiyorum.
  key_name = "victus_key_0"
}

data "aws_ami" "my_ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical'in resmi owner ID'si (normalde sen resourse ile oluştur şimdilik böyle yapıyom)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "web_server" {
  ami                    = data.aws_ami.my_ubuntu.id
  instance_type          = "t3.micro"
  key_name               = data.aws_key_pair.existing_key.key_name
  subnet_id = module.networking.public_subnet_id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name = "${var.project_name}-${terraform.workspace}-web-server-tf"
  }
}

module "networking" {
  source       = "./modules/networking"
  project_name = var.project_name
}