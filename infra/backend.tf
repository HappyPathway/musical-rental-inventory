terraform {
  backend "gcs" {
    bucket  = "roknsound-tfstate"
    prefix  = "terraform/infra"
  }
}
