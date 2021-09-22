provider "aws" {
  region = "eu-central-1"
}

resource "aws_s3_bucket" "mono_terraform_state" {
  bucket = "mono-devops-terraform-state"
  acl = "private"

  # allow delete bucket with things in it
  force_destroy = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "no_public_access_to_bucket" {
  bucket = aws_s3_bucket.mono_terraform_state.id

  block_public_acls   = true
  block_public_policy = true
}
