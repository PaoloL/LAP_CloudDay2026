variable "container_image" {
  description = "URI immagine container dell'API (es. <account>.dkr.ecr.eu-west-1.amazonaws.com/garage-management:1.0.0)"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ARN certificato ACM per il listener HTTPS dell'ALB interno"
  type        = string
}

variable "alb_internal_domain_name" {
  description = "Nome DNS coperto dal certificato ACM, usato da API Gateway per verificare il TLS verso l'ALB"
  type        = string
}

variable "log_retention_days" {
  description = "Retention dei log CloudWatch"
  type        = number
  default     = 365
}
