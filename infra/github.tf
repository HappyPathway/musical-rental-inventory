# GitHub repository configuration

# Testing Milestone
resource "github_repository_milestone" "testing_milestone" {
  repository  = "musical-rental-inventory"
  title       = "Complete Testing Coverage"
  description = "Achieve comprehensive test coverage across all major features"
  due_date    = timeadd(timestamp(), "720h") # 30 days from creation
  owner       = "HappyPathway"
}

# Issue Labels
resource "github_issue_label" "testing" {
  repository  = "musical-rental-inventory"
  name        = "testing"
  color       = "1d76db"
  description = "Testing related tasks and issues"
}

resource "github_issue_label" "authentication" {
  repository  = "musical-rental-inventory"
  name        = "authentication"
  color       = "0e8a16"
  description = "Authentication and user management"
}

resource "github_issue_label" "equipment" {
  repository  = "musical-rental-inventory"
  name        = "equipment"
  color       = "d93f0b"
  description = "Equipment management and inventory"
}

resource "github_issue_label" "rentals" {
  repository  = "musical-rental-inventory"
  name        = "rentals"
  color       = "fbca04"
  description = "Rental process and management"
}

resource "github_issue_label" "workflow" {
  repository  = "musical-rental-inventory"
  name        = "workflow"
  color       = "5319e7"
  description = "Business process workflows"
}

resource "github_issue_label" "management" {
  repository  = "musical-rental-inventory"
  name        = "management"
  color       = "b60205"
  description = "Administrative management features"
}