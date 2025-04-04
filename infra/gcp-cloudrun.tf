# Google Cloud Run configuration

# Cloud Run service
resource "google_cloud_run_service" "app" {
  name     = "roknsound-rental-inventory"
  location = var.region
  
  template {
    spec {
      containers {
        # Use the Docker image we've pushed to Artifact Registry
        image = "${var.region}-docker.pkg.dev/${var.project_id}/roknsound-images/roknsound-rental-inventory:latest"
        
        env {
          name  = "DJANGO_SECRET_KEY"
          value = random_password.django_secret.result
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgres://${google_sql_user.app_user.name}:${google_sql_user.app_user.password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.roknsound_db.name}"
        }
        
        env {
          name  = "GS_BUCKET_NAME"
          value = google_storage_bucket.media_bucket.name
        }
        
        env {
          name  = "GS_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "DEBUG"
          value = "0"
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

# Cloud Run job for migrations
resource "google_cloud_run_v2_job" "migrations" {
  provider = google-beta
  name     = "roknsound-migrations"
  location = var.region
  deletion_protection = false

  template {
    template {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/roknsound-images/roknsound-rental-inventory:latest"
        
        env {
          name  = "DJANGO_SECRET_KEY"
          value = random_password.django_secret.result
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgres://${google_sql_user.app_user.name}:${google_sql_user.app_user.password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.roknsound_db.name}"
        }
        
        env {
          name  = "GS_BUCKET_NAME"
          value = google_storage_bucket.media_bucket.name
        }
        
        env {
          name  = "GS_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "DEBUG"
          value = "0"
        }
        
        env {
          name  = "MIGRATE_ONLY"
          value = "1"
        }
      }

      service_account = google_service_account.app_service_account.email
    }
  }
}