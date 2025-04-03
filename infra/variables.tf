# This file intentionally left empty as variables are defined in main.tf

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "happypathway-1522441039906" # Replace with your actual project ID
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "django_secret_key" {
  description = "Secret key for Django application"
  type        = string
  sensitive   = true
  # Don't set a default value for sensitive data
  # Default will be provided via terraform.tfvars or environment variable
}

variable "database_url" {
  description = "Database connection URL (e.g., for Cloud SQL)"
  type        = string
  sensitive   = true
  default     = "sqlite:///db.sqlite3" # Default for local/testing, override for production
}

variable "bucket_name" {
  description = "Name of the GCS bucket for media storage"
  type        = string
  default     = "roknsound-music-rental-inventory"
}

variable "github_token" {
  description = "GitHub Personal Access Token"
  type        = string
  sensitive   = true
}
