variable "project_id" {
  description = "The Google Cloud project ID."
  type        = string
}

variable "location" {
  description = "The Google Cloud location (region) for the GCS bucket."
  type        = string
  default     = "US-CENTRAL1"
}

variable "state_bucket_name" {
  description = "The desired name for the GCS bucket to store Terraform state."
  type        = string
  # Example: roknsound-tf-state-YOUR_PROJECT_ID
}
