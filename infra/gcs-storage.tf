# Google Cloud Storage bucket for media files
resource "google_storage_bucket" "media_bucket" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30 # days
    }
    action {
      type = "Delete"
    }
  }
}

# Service account for the application


# Grant the service account access to the bucket
resource "google_storage_bucket_iam_member" "bucket_access" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.app_service_account.email}"
}
