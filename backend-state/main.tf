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
  for_each = toset([var.state_bucket_name, "${var.state_bucket_name}-logs"])
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
    bucket  = "${lookup(google_storage_bucket.terraform_state, var.state_bucket_name).name}"
    prefix  = "terraform/infra"
  }
}
EOT
}

# GitHub repository connection for Cloud Build
resource "google_cloudbuildv2_repository" "github_repo" {
  name              = "musical-rental-inventory"
  parent_connection = google_cloudbuildv2_connection.github_connection.name
  remote_uri        = "https://github.com/HappyPathway/musical-rental-inventory.git"
  location          = var.location
}

# GitHub connection for Cloud Build
resource "google_cloudbuildv2_connection" "github_connection" {
  name     = "github-connection"
  location = var.location
  
  github_config {
    app_installation_id = data.google_secret_manager_secret_version.github_app_installation_id.secret_data
    authorizer_credential {
      oauth_token_secret_version = data.google_secret_manager_secret_version.github_oauth_token.id
    }
  }
}

# Data sources for GitHub secrets
data "google_secret_manager_secret_version" "github_app_installation_id" {
  secret  = "github-app-installation-id"
  version = "latest"
  project = var.project_id
}

data "google_secret_manager_secret_version" "github_oauth_token" {
  secret  = "github-oauth-token"
  version = "latest"
  project = var.project_id
}
