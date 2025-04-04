# Google Cloud Storage bucket for media files
resource "google_storage_bucket" "media_bucket" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Service account for the application


# Grant the service account access to the bucket
resource "google_storage_bucket_iam_binding" "bucket_access" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectAdmin"
  members = [
    "serviceAccount:${google_service_account.app_service_account.email}"
  ]
}
