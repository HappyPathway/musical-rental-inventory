terraform {
  backend "s3" {
    bucket = "roknsound-terraform-state" # Replace with your actual S3 bucket name
    key    = "infra/terraform.tfstate"
    region = "us-east-1"               # Replace with your desired AWS region
    # Optionally add dynamodb_table = "roknsound-terraform-locks" for state locking
  }
}
