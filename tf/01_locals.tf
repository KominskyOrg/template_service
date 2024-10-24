locals {
  stack_name        = "stack"
  microservice_type = "service"
  node_selector     = "backend"


  tags = {
    env     = var.env
    service = local.service_name
  }
  env               = var.env
  service_name      = "${local.stack_name}_${local.microservice_type}"
}