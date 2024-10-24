variable "image_tag" {
  description = "Docker image tag for stack's service"
  type        = string
  default     = "latest"
}

variable "replicas" {
  description = "Number of replicas for stack's service"
  type        = number
  default     = 1
}

variable "env" {
  description = "Environment name"
  type        = string
  default     = "staging"
}
