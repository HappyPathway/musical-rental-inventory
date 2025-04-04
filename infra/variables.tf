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

variable "bucket_name" {
  description = "Name of the GCS bucket for media storage"
  type        = string
  default     = "roknsound-music-rental-inventory"
}
