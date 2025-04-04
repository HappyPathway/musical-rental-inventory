# GitHub issues using external markdown files for body content

# Create all issues using for_each loop
resource "github_issue" "all_issues" {
  for_each    = { for issue in local.issues : issue.key => issue }
  
  repository  = "musical-rental-inventory"
  title       = each.value.title
  
  # Read body content from Markdown file, with fallback if file doesn't exist yet
  body        = fileexists("${path.module}/issues/${each.key}.md") ? file("${path.module}/issues/${each.key}.md") : "TODO: Create content for ${each.key}.md"
  
  # Convert labels from list to proper format
  labels      = each.value.labels
  depends_on  = [
    github_repository_milestone.testing_milestone,
    github_issue_label.all_labels
  ]
}
