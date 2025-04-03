terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
}

# GCS bucket for storing the main infrastructure's Terraform state
resource "google_storage_bucket" "terraform_state" {
  name          = var.state_bucket_name
  location      = var.location
  storage_class = "STANDARD"
  force_destroy = false # Protects state

  # Enable versioning for state history and recovery
  versioning {
    enabled = true
  }

  # Prevent accidental public access
  public_access_prevention = "enforced"

  # Enforce uniform bucket-level access for better security
  uniform_bucket_level_access = true
}

# Generate the backend configuration file for the main infrastructure
resource "local_file" "infra_backend_config" {
  filename = "../infra/backend.tf" # Path relative to the backend-state directory
  content  = <<-EOT
terraform {
  backend "gcs" {
    bucket  = "${google_storage_bucket.terraform_state.name}"
    prefix  = "terraform/state"
  }
}
EOT
}
