provider "google" {
  # Configuration options
}

resource "google_storage_bucket" "media_bucket" {
  name          = "roknsound-music-rental-inventory"
  location      = "US-CENTRAL1" # Or your preferred region
  storage_class = "STANDARD"
  force_destroy = false # Set to true to allow deletion of non-empty buckets during terraform destroy

  # Optional: Configure uniform bucket-level access
  uniform_bucket_level_access = true

  # Optional: Lifecycle rules (e.g., delete old objects)
  # lifecycle_rule {
  #   condition {
  #     age = 30 # days
  #   }
  #   action {
  #     type = "Delete"
  #   }
  # }

  # Optional: CORS configuration if accessed directly from browsers
  # cors {
  #   origin          = ["http://example.com"]
  #   method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
  #   response_header = ["*"]
  #   max_age_seconds = 3600
  # }
}

# Add outputs if needed, e.g., the bucket name or URL
output "media_bucket_name" {
  value = google_storage_bucket.media_bucket.name
}

output "media_bucket_url" {
  value = google_storage_bucket.media_bucket.url
}
