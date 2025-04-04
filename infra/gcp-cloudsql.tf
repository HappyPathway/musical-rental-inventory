# Google Cloud SQL configuration

# Generate a secure database password
resource "random_password" "database_password" {
  length  = 24
  special = false
}

# Cloud SQL instance - smallest available (db-f1-micro)
resource "google_sql_database_instance" "postgres" {
  name             = "roknsound-db-instance"
  database_version = "POSTGRES_14"
  region           = var.region
  
  settings {
    tier              = "db-f1-micro"  # Smallest, cheapest tier
    availability_type = "ZONAL"        # Zonal for lower cost
    
    ip_configuration {
      # Public IP for simplicity, but you may want to use private IP in production
      ipv4_enabled = true
      
      # Allow Cloud Run service to connect
      authorized_networks {
        name  = "all-networks"  # Allow from anywhere (Cloud Run has dynamic IPs)
        value = "0.0.0.0/0"
      }
    }
    
    # Enable point-in-time recovery
    backup_configuration {
      enabled            = true
      start_time         = "02:00"  # 2 AM UTC
      point_in_time_recovery_enabled = true
    }
  }
  
  # Allow deletion without manual intervention (for dev environments)
  deletion_protection = false
}

# Create database
resource "google_sql_database" "roknsound_db" {
  name     = "roknsound"
  instance = google_sql_database_instance.postgres.name
}

# Create database user
resource "google_sql_user" "app_user" {
  name     = "roknsound_app"
  instance = google_sql_database_instance.postgres.name
  password = random_password.database_password.result  # Using separate password for database
}