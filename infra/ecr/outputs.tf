output "repository_url" {
  description = "Docker pull/push URI for the realtime-backend repository."
  value       = aws_ecr_repository.realtime_backend.repository_url
}

output "repository_arn" {
  description = "ARN of the ECR repository."
  value       = aws_ecr_repository.realtime_backend.arn
}

output "repository_name" {
  description = "ECR repository name (for aws ecr describe-images)."
  value       = aws_ecr_repository.realtime_backend.name
}
