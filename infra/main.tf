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

# Grant public read access to the media bucket
resource "google_storage_bucket_iam_binding" "media_bucket_public_read" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectViewer"
  members = [
    "allUsers",
  ]
}


# Create a service account for the application
resource "google_service_account" "app_service_account" {
  account_id   = "roknsound-storage-sa"
  display_name = "ROKNSOUND Storage Service Account"
  project      = "happypathway-1522441039906" # Replace with your project ID
}

# Grant the service account permissions on the bucket
resource "google_storage_bucket_iam_member" "app_sa_bucket_admin" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectAdmin" # Permissions to manage objects
  member = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Create a key for the service account
resource "google_service_account_key" "app_service_account_key" {
  service_account_id = google_service_account.app_service_account.name
  public_key_type    = "TYPE_X509_PEM_FILE" # Or other types if needed
}

# Save the service account key to a local file
resource "local_file" "service_account_key_file" {
  content  = base64decode(google_service_account_key.app_service_account_key.private_key)
  filename = "${path.module}/../gcp-service-account-key.json" # Save in the infra directory
}
