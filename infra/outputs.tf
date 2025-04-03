# Add outputs if needed, e.g., the bucket name or URL
output "media_bucket_name" {
  value = google_storage_bucket.media_bucket.name
}

output "media_bucket_url" {
  value = google_storage_bucket.media_bucket.url
}

# Output the path to the key file (useful for setting env vars)
output "service_account_key_file_path" {
  value = local_file.service_account_key_file.filename
}

output "milestone_url" {
  description = "URL of the testing milestone"
  value       = "https://github.com/HappyPathway/musical-rental-inventory/milestone/${github_repository_milestone.testing_milestone.number}"
}

output "milestone_title" {
  description = "Title of the testing milestone"
  value       = github_repository_milestone.testing_milestone.title
}

output "milestone_due_date" {
  description = "Due date of the testing milestone"
  value       = github_repository_milestone.testing_milestone.due_date
}

# Cloud Run and Database outputs
output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.app.status[0].url
}

output "database_instance_name" {
  description = "Name of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.name
}

output "database_connection_name" {
  description = "Connection name for the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.connection_name
}

output "database_url" {
  description = "Database connection URL"
  value       = "postgres://${google_sql_user.app_user.name}:${google_sql_user.app_user.password}@${google_sql_database_instance.postgres.public_ip_address}:5432/${google_sql_database.roknsound_db.name}"
  sensitive   = true
}

output "django_secret_key" {
  description = "Generated Django secret key"
  value       = random_password.django_secret.result
  sensitive   = true
}
