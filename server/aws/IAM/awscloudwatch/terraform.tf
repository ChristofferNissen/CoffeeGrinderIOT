terraform {
  # configure s3 backend
  # variables are not allowed in this config block
  # as variables are created after terraform initialization
  # therefore YOU MUST ENSURE THAT THEY ARE CORRECT!
  backend "s3" {
    bucket = "mono-devops-terraform-state"
    # key is name of the terraform state file
    key = "mono_terraform_state_grafana_aws_IAM.tfstate"
    region = "eu-central-1"
  }
}