terraform {
  backend "gcs" {
    bucket = "hpw-terraform-state"
    prefix = "music-rental-inventory"
  }
}
