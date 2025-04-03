# Main Terraform configuration file
# Contains shared resources and those that don't fit elsewhere

# Generate a random password for Django secret key
resource "random_password" "django_secret" {
  length  = 32
  special = true
}
