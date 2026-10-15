output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes version running on the cluster."
  value       = module.eks.cluster_version
}

output "aws_region" {
  description = "Region where the cluster runs."
  value       = var.aws_region
}

output "configure_kubectl" {
  description = "Command to merge kubeconfig for this cluster."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "node_instance_types" {
  description = "CPU instance types on the managed node group."
  value       = var.node_instance_types
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group for realtime-backend stdout (P6-006)."
  value       = aws_cloudwatch_log_group.realtime_backend.name
}
