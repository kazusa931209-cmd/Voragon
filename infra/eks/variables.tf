variable "aws_region" {
  description = "AWS region (match infra/ecr and image pushes)."
  type        = string
  default     = "ap-northeast-1"
}

variable "cluster_name" {
  description = "EKS cluster name (staging/non-prod)."
  type        = string
  default     = "voragon-staging"
}

variable "cluster_version" {
  description = "EKS Kubernetes version."
  type        = string
  default     = "1.31"
}

variable "vpc_cidr" {
  description = "VPC CIDR for the EKS cluster."
  type        = string
  default     = "10.0.0.0/16"
}

variable "node_instance_types" {
  description = "CPU instance types for the managed node group."
  type        = list(string)
  default     = ["m6i.large"]
}

variable "node_desired_size" {
  description = "Desired worker count (staging default: 1)."
  type        = number
  default     = 1
}

variable "node_min_size" {
  type    = number
  default = 1
}

variable "node_max_size" {
  type    = number
  default = 3
}
