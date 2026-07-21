terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

   backend "s3" {
    bucket = "furkan-terraform-state-2121"
    key    = "autopilot-infra/terraform.tfstate"
    region = "eu-north-1"
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-web-sg-tf"
  description = "SSH ve HTTP erisimi icin"
  vpc_id      = module.networking.vpc_id

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

  ingress {
    description = "FastAPI container port"
    from_port   = 8000
    to_port     = 8000
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
  subnet_id              = module.networking.public_subnet_id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name = "${var.project_name}-${terraform.workspace}-web-server-tf"
  }
}

module "networking" {
  source       = "./modules/networking"
  project_name = var.project_name
}

resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-fastapi-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true  # Bu satırı ekledik

  tags = {
    Name = "${var.project_name}-ecr"
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecsTaskExecutionRole-tf"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "fastapi-container"
      image     = "${aws_ecr_repository.app.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}-task"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}-task"
  retention_in_days = 7
}

resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [module.networking.public_subnet_id]
    security_groups  = [aws_security_group.web_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "fastapi-container"
    container_port   = 8000
  }
}

resource "aws_lb" "app" {
  name               = "${var.project_name}-alb-tf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web_sg.id]
  subnets            = [
    module.networking.public_subnet_id,
    module.networking.public_subnet_2_id
  ]
}

resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-tg-tf"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.networking.vpc_id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}