# Google Cloud Run configuration

# Cloud Run service
resource "google_cloud_run_service" "app" {
  name     = "roknsound-app"
  location = var.region
  
  template {
    spec {
      containers {
        #
        image = "gcr.io/${var.project_id}/roknsound-app:latest"  # You'll need to build and push this image
        
        env {
          name  = "DJANGO_SECRET_KEY"
          value = random_password.django_secret.result
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgres://${google_sql_user.app_user.name}:${google_sql_user.app_user.password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.roknsound_db.name}"
        }
        
        env {
          name  = "GCS_BUCKET_NAME"
          value = google_storage_bucket.media_bucket.name
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
      
      service_account_name = google_service_account.app_service_account.email
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM binding for Cloud Run - make service publicly accessible
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.app.name
  location = google_cloud_run_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"  # Public access - anyone can access the app
}