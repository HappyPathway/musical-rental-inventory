resource "google_service_account" "app_service_account" {
  account_id   = "roknsound-storage-sa"
  display_name = "Service Account for ROKNSOUND Rental Inventory"
  description  = "Service account for accessing GCS bucket and other GCP services"
}

# Create and download service account key
resource "google_service_account_key" "app_service_account_key" {
  service_account_id = google_service_account.app_service_account.name
}

# Save the service account key to a file
resource "local_file" "service_account_key_file" {
  content  = base64decode(google_service_account_key.app_service_account_key.private_key)
  filename = "${path.module}/../gcp-service-account-key.json"
}

# Additional IAM permissions for the service account to access Cloud SQL
resource "google_project_iam_member" "cloud_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Storage Object Admin permission for accessing the GCS bucket
resource "google_project_iam_member" "storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Storage Admin permission for managing the GCS bucket
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Cloud Run Admin permission for deploying to Cloud Run
resource "google_project_iam_member" "run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# IAM permission for the service account to act as itself
resource "google_service_account_iam_binding" "app_service_account_user" {
  service_account_id = google_service_account.app_service_account.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "serviceAccount:${google_service_account.app_service_account.email}",
  ]
}
