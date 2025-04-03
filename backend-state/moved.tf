moved {
  from = google_storage_bucket.terraform_state
  to = google_storage_bucket.terraform_state[var.state_bucket_name] 
}