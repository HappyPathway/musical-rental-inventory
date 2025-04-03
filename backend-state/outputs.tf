output bucket_name {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}"].name
}

output logging_bucket_name {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}-logs"].name
}

output bucket_location {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}"].location
}

output bucket_location_logging {
  value = google_storage_bucket.terraform_state["${var.state_bucket_name}-logs"].location
}