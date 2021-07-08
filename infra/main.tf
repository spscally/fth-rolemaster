terraform {
  required_providers {
    aws = "~> 3.27"
  }
  
  required_version = ">= 0.12"
}

provider "aws" {
    profile = "prod"
    region = "us-east-1"
}

resource "aws_lambda_function" "rolemaster_lambda" {
    // TODO: fill out the rest of this. Also: create a role?
}