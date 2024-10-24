resource "aws_ecr_repository" "app_ecr" {
  name                 = "${local.service_name}_${local.env}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}
