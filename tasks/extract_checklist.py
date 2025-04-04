#!/usr/bin/env python3
"""
Script to extract testing checklist items and create issue markdown files.
Also updates issues.yaml and labels.yaml with the extracted information.
"""
import os
import re
import yaml
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parent
ISSUES_DIR = BASE_DIR / "issues"
CHECKLIST_PATH = BASE_DIR.parent / "docs" / "testing_checklist.md"

# Ensure issues directory exists
ISSUES_DIR.mkdir(exist_ok=True)

def parse_testing_checklist():
    """Parse the testing checklist and create issue markdown files"""
    # Clean up any existing files
    for f in ISSUES_DIR.glob("*.md"):
        f.unlink()
    for f in ISSUES_DIR.glob("*.yaml"):
        f.unlink()
        
    # Read the testing checklist
    print(f"Reading testing checklist from {CHECKLIST_PATH}")
    with open(CHECKLIST_PATH, 'r') as f:
        content = f.read()
    
    # Dictionary to store all issues
    all_issues = []
    
    # Extract section-subsection structure
    pattern = r'## ([^\n]+)(.*?)(?=\n## |$)'
    for section_match in re.finditer(pattern, content, re.DOTALL):
        section = section_match.group(1)
        section_content = section_match.group(2)
        
        # Skip the non-test sections
        if section in ["Notes", "Sign-off"]:
            continue
        
        # Find subsections in this section
        subsection_pattern = r'### ([^\n]+)(.*?)(?=\n### |$)'
        for subsection_match in re.finditer(subsection_pattern, section_content, re.DOTALL):
            subsection = subsection_match.group(1)
            subsection_content = subsection_match.group(2).strip()
            
            # Create issue key
            section_key = clean_name(section)
            subsection_key = clean_name(subsection)
            issue_key = f"{section_key}_{subsection_key}"
            
            # Create issue markdown
            create_issue_markdown(issue_key, section, subsection, subsection_content)
            
            # Add to issues list
            labels = derive_labels(section, subsection)
            all_issues.append({
                "key": issue_key,
                "title": f"[Test] {section} - {subsection}",
                "labels": labels
            })
    
    # Update YAML files
    update_issues_yaml(all_issues)
    update_labels_yaml()
    
    print(f"Created {len(all_issues)} issues")
    return all_issues

def create_issue_markdown(issue_key, section, subsection, content):
    """Create a markdown file for an issue"""
    md_file_path = ISSUES_DIR / f"{issue_key}.md"
    
    # Format the markdown content
    md_content = f"## Test Cases\n\n"
    
    # Extract all checklist items with proper indentation
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('- [ ]'):
            md_content += line + '\n'
    
    # Add notes section
    md_content += f"\n## Notes\n"
    md_content += f"- Document any failures or unexpected behavior\n"
    md_content += f"- Test with different user roles where applicable\n"
    md_content += f"- Verify all UI elements follow the ROKNSOUND design guidelines\n"
    
    # Write to file
    with open(md_file_path, 'w') as f:
        f.write(md_content)
    
    print(f"Created {md_file_path}")

def clean_name(name):
    """Convert a name to a valid file name and variable name"""
    # Remove non-alphanumeric characters and replace spaces with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', name).lower().replace(' ', '_')
    return cleaned

def derive_labels(section, subsection):
    """Derive appropriate labels based on section and subsection"""
    labels = ["testing"]
    
    # Add section-based label
    section_map = {
        "Authentication Workflows": "authentication",
        "Equipment Management": "equipment",
        "Rental Management": "rentals",
        "User Management": "management",
        "Payment Processing": "payments",
        "System Administration": "management",
        "Mobile Responsiveness": "mobile",
        "Error Handling": "workflow",
        "Performance Testing": "testing",
        "Security Testing": "security"
    }
    
    if section in section_map:
        labels.append(section_map[section])
    
    # Add subsection-specific labels
    if any(word in subsection.lower() for word in ["ui", "interface", "responsive"]):
        labels.append("ui")
    if any(word in subsection.lower() for word in ["search", "find"]):
        labels.append("search")
    if any(word in subsection.lower() for word in ["workflow", "process"]):
        labels.append("workflow")
    if any(word in subsection.lower() for word in ["checkout", "payment"]):
        labels.append("checkout")
    if any(word in subsection.lower() for word in ["report", "analytics"]):
        labels.append("reports")
    
    return labels

def update_issues_yaml(all_issues):
    """Update the issues.yaml file with all extracted issues"""
    issues_yaml_path = ISSUES_DIR / "issues.yaml"
    
    # Create the issues YAML structure
    issues_data = {"issues": all_issues}
    
    # Write to file
    with open(issues_yaml_path, 'w') as f:
        yaml.dump(issues_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {issues_yaml_path}")

def update_labels_yaml():
    """Update the labels.yaml file with all necessary labels"""
    labels_yaml_path = ISSUES_DIR / "labels.yaml"
    
    # Define all labels
    labels = [
        {"name": "testing", "color": "1d76db", "description": "Testing related tasks and issues"},
        {"name": "authentication", "color": "0e8a16", "description": "Authentication and user management"},
        {"name": "equipment", "color": "d93f0b", "description": "Equipment management and inventory"},
        {"name": "rentals", "color": "fbca04", "description": "Rental process and management"},
        {"name": "workflow", "color": "5319e7", "description": "Business process workflows"},
        {"name": "management", "color": "b60205", "description": "Administrative management features"},
        {"name": "ui", "color": "cc317c", "description": "User interface elements and design"},
        {"name": "mobile", "color": "0052cc", "description": "Mobile-specific functionality and testing"},
        {"name": "reports", "color": "006b75", "description": "Reporting and analytics features"},
        {"name": "security", "color": "ee0701", "description": "Security features and testing"},
        {"name": "search", "color": "c2e0c6", "description": "Search functionality and optimization"},
        {"name": "checkout", "color": "fef2c0", "description": "Checkout and order processing"},
        {"name": "payments", "color": "c5def5", "description": "Payment processing and management"}
    ]
    
    # Create the labels YAML structure
    labels_data = {"labels": labels}
    
    # Write to file
    with open(labels_yaml_path, 'w') as f:
        yaml.dump(labels_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {labels_yaml_path}")

if __name__ == "__main__":
    parse_testing_checklist()