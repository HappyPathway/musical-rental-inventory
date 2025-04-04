# GitHub repository configuration
locals {
  # Load issue labels from YAML file
  labels_data = yamldecode(file("${path.module}/issues/labels.yaml"))
  labels = local.labels_data.labels
  
  # Load issues from YAML file
  issues_data = yamldecode(file("${path.module}/issues/issues.yaml"))
  issues = local.issues_data.issues
}

# Testing Milestone
resource "github_repository_milestone" "testing_milestone" {
  repository  = "musical-rental-inventory"
  title       = "Complete Testing Coverage"
  description = "Achieve comprehensive test coverage across all major features"
  due_date    = "2025-05-03"
  owner       = "HappyPathway"
}

# Create all labels using for_each
resource "github_issue_label" "all_labels" {
  for_each    = { for label in local.labels : label.name => label }
  repository  = "musical-rental-inventory"
  name        = each.value.name
  color       = each.value.color
  description = each.value.description
}