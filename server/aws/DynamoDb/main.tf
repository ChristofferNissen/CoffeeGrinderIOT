provider "aws" {
  region = "eu-central-1"
}

resource "aws_dynamodb_table" "loki_index" {
  name           = "LokiIndexes"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "h"
  range_key      = "r"

  attribute {
    name = "h"
    type = "S"
  }

  attribute {
    name = "r"
    type = "B"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }

  # global_secondary_index {
  #   name               = "GameTitleIndex"
  #   hash_key           = "GameTitle"
  #   range_key          = "TopScore"
  #   write_capacity     = 10
  #   read_capacity      = 10
  #   projection_type    = "INCLUDE"
  #   non_key_attributes = ["UserId"]
  # }

  tags = {
    Name        = "dynamodb-table-1"
    Environment = "production"
  }
}