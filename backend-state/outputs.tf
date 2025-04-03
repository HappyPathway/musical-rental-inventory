output bucket_name {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}"].name
}

output logging_bucket_name {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}-logs"].name
}

output bucket_location {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}"].location
}

output bucket_location_logging {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}-logs"].location
}

output "state_bucket_name" {
  value = var.state_bucket_name
}

output "location" {
  value = var.location
}

# Cloud Build V2 Repository outputs
output "cloudbuild_repository_id" {
  value       = google_cloudbuildv2_repository.github_repo.id
  description = "ID of the Cloud Build V2 repository"
}

output "cloudbuild_repository_name" {
  value       = google_cloudbuildv2_repository.github_repo.name
  description = "Name of the Cloud Build V2 repository"
}

output "github_connection_id" {
  value       = google_cloudbuildv2_connection.github_connection.id
  description = "ID of the GitHub connection for Cloud Build"
}