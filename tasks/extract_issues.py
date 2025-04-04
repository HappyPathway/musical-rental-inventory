#!/usr/bin/env python
"""
Script to extract issue bodies from old issues.tf and create markdown files.
This helps migrate to the new system that stores issue bodies in separate files.
"""
import os
import re
import sys

# Directory to store issue markdown files
ISSUES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "issues")

def extract_issues():
    """Extract issue bodies from issues.tf and create markdown files"""
    # Make sure the issues directory exists
    os.makedirs(ISSUES_DIR, exist_ok=True)
    
    # Path to the old issues.tf file
    issues_tf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "issues.tf.bak")
    
    if not os.path.exists(issues_tf_path):
        print(f"Error: {issues_tf_path} not found.")
        print("Please rename your original issues.tf to issues.tf.bak first.")
        sys.exit(1)
    
    # Read the issues.tf file
    with open(issues_tf_path, 'r') as f:
        content = f.read()
    
    # Regular expression pattern to extract issue resources and their body content
    pattern = r'resource\s+"github_issue"\s+"([^"]+)"\s+{[^}]*body\s+=\s+<<-EOT(.*?)EOT'
    matches = re.findall(pattern, content, re.DOTALL)
    
    # Create a markdown file for each issue
    for issue_key, body in matches:
        # Clean up the body text
        body = body.strip()
        
        # Create markdown file
        md_file_path = os.path.join(ISSUES_DIR, f"{issue_key}.md")
        with open(md_file_path, 'w') as f:
            f.write(body)
        
        print(f"Created {md_file_path}")
    
    print(f"\nCreated {len(matches)} issue markdown files in {ISSUES_DIR}")

if __name__ == "__main__":
    extract_issues()