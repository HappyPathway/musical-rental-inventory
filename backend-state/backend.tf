# backend-state/backend.tf

# Initially, manage the state for this bucket locally.
# You can configure a remote backend (like another GCS bucket)
# for this specific configuration later if needed.
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
