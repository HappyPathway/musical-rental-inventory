
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