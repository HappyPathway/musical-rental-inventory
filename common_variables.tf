variable "project_id" {
  description = "The Google Cloud project ID."
  type        = string
  # This value should be provided via a .tfvars file or environment variable
}

variable "location" {
  description = "The primary Google Cloud location (region) for resources."
  type        = string
  default     = "us-central1"
}
