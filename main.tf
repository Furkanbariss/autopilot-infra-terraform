terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
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

module "networking" {
  source       = "./modules/networking"
  project_name = var.project_name
}

resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-fastapi-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Bu satırı ekledik

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

      # Hassas olmayan degerler: normal environment variable
      environment = [
        {
          name  = "DB_HOST"
          value = aws_db_instance.main.address # endpoint degil, address (port'suz hali)
        },
        {
          name  = "DB_PORT"
          value = "5432"
        },
        {
          name  = "DB_NAME"
          value = "autopilot"
        }
      ]

      # Hassas degerler: Secrets Manager'dan cekilir
      secrets = [
        {
          name      = "DB_USER"
          valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:username::"
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:password::"
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
  name                               = "${var.project_name}-service"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.app.arn
  desired_count                      = 1
  launch_type                        = "FARGATE"
  deployment_minimum_healthy_percent = 100 # deployment sirasinda her zaman en az %100 kapasite ayakta kalsin
  deployment_maximum_percent         = 200 # gecici olarak 2 katina kadar cikabilsin (eski + yeni ayni anda)

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
  subnets = [
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

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "xxxxxxxxxxxxxxxxxx@gmail.com"
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.project_name}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2 # 2 ardisik periyot esigi asarsa tetiklen
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60 # 60 saniyelik periyotlar
  statistic           = "Average"
  threshold           = 85 # %85 esigi
  alarm_description   = "ECS service CPU kullanimi %85'i asti"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn] # tetiklenince SNS'e haber ver
  ok_actions    = [aws_sns_topic.alerts.arn] # normale donunce de haber ver
}

resource "aws_iam_role" "lambda_autoscaler_role" {
  name = "${var.project_name}-lambda-autoscaler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Lambda'nin kendi loglarini yazabilmesi icin
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_autoscaler_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Least-privilege: sadece gereken CloudWatch ve ECS izinleri
resource "aws_iam_role_policy" "lambda_autoscaler_policy" {
  name = "${var.project_name}-lambda-autoscaler-policy"
  role = aws_iam_role.lambda_autoscaler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadCloudWatchMetrics"
        Effect   = "Allow"
        Action   = ["cloudwatch:GetMetricStatistics"]
        Resource = "*"
      },
      {
        Sid    = "ManageEcsService"
        Effect = "Allow"
        Action = [
          "ecs:DescribeServices",
          "ecs:UpdateService"
        ]
        Resource = aws_ecs_service.app.id # SADECE bu service'i yonetebilir
      }
    ]
  })
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_autoscaler/lambda_function.py"
  output_path = "${path.module}/lambda_autoscaler/lambda_function.zip"
} # bu data nereye gidiyor?

resource "aws_lambda_function" "autoscaler" {
  function_name    = "${var.project_name}-lambda-autoscaler"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256 #Terraform'un kodun değişip değişmediğini anlamasını sağlar. bunuda hash koduna çevirerek bakar eski hash kodu ile yenisi aynıysa değişiklik yokder devam eder.
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.13"
  role             = aws_iam_role.lambda_autoscaler_role.arn
  timeout          = 30 # normalde varsayılan 3 öneriliyor interneete fakat ben deneme amaçlı 3 yapıcam faturayı dengelemeni sağlar.

  tags = {
    Name = "${var.project_name}-autoscaler"
  }
}

#2 dakikada bir çalıcak alarm kurduk
resource "aws_cloudwatch_event_rule" "autoscaler_schedule" {
  name                = "${var.project_name}-autoscaler-schedule"
  description         = "Autoscaler Lambda'yi periyodik tetikler"
  schedule_expression = "rate(2 minutes)"
}

# bu alarmı lambdaya bağladık
resource "aws_cloudwatch_event_target" "autoscaler_target" {
  rule      = aws_cloudwatch_event_rule.autoscaler_schedule.name
  target_id = "autoscaler_lambda"
  arn       = aws_lambda_function.autoscaler.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.autoscaler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.autoscaler_schedule.arn
}

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-db-subnet-group"
  subnet_ids = [
    module.networking.private_subnet_2_id,
    module.networking.private_subnet_id
  ]

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "RDS erisimi - sadece ECS tasklarindan"
  vpc_id      = module.networking.vpc_id

  ingress {
    description     = "PostgreSQL from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id] # belirli bir ip aralığı vermektense ECS security group'undan gelmesi daha mantıklı dedik.
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?" # RDS bu karakterleri kabul etmediği için almadım
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}-db-credentials"
  description             = "RDS PostgreSQL baglanti bilgileri"
  recovery_window_in_days = 0 #Öğrenme ortamında 0 yapmak pratik; production'da bunu asla yapma (yanlışlıkla silinen bir secret geri getirilemez).
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = "autopilot_admin"
    password = random_password.db_password.result
    dbname   = "autopilot"
  })
}

resource "aws_iam_role_policy" "ecs_secrets_access" {
  name = "${var.project_name}-ecs-secrets-access"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.db_credentials.arn]
    }]
  })
}

resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.micro" # Free Tier uyumlu

  allocated_storage     = 20 # GB, Free Tier limiti
  max_allocated_storage = 50 # otomatik buyume tavani
  storage_type          = "gp2"
  storage_encrypted     = true # at-rest sifreleme

  db_name  = "autopilot"
  username = "autopilot_admin"
  password = random_password.db_password.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = false # KRITIK: internete kapali

  backup_retention_period = 1     # 1 gun yedek (ogrenme ortami)
  skip_final_snapshot     = true  # destroy sirasinda snapshot alma (ogrenme ortami)
  deletion_protection     = false # ogrenme ortami: silinebilsin

  tags = {
    Name = "${var.project_name}-rds"
  }
}
