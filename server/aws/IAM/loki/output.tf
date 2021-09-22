output "loki_role_arn" {
  value       = aws_iam_role.loki_role.arn
  description = "The public DNS name of the EC2 server instance. (aws_eip)"

  depends_on = [
    # Security group rule must be created before this IP address could
    # actually be used, otherwise the services will be unreachable.
    aws_iam_role.loki_role
  ]
}