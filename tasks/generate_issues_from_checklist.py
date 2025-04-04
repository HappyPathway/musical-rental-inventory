#!/usr/bin/env python
"""
Script to extract testing checklist items and create corresponding issue markdown files.
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
    # Read the testing checklist
    with open(CHECKLIST_PATH, 'r') as f:
        content = f.read()
    
    # Dictionary to store all issues
    all_issues = []
    
    # Find all sections
    sections = re.findall(r'## ([^\n]+)', content)
    
    for section in sections:
        # Get the content for this section
        section_match = re.search(f'## {re.escape(section)}(.*?)(?=\n## |$)', content, re.DOTALL)
        if not section_match:
            continue
            
        section_content = section_match.group(1)
        
        # Find all subsections in this section
        subsections = re.findall(r'### ([^\n]+)', section_content)
        
        for subsection in subsections:
            # Get the content for this subsection
            subsection_match = re.search(f'### {re.escape(subsection)}(.*?)(?=\n### |$)', section_content, re.DOTALL)
            if not subsection_match:
                continue
                
            subsection_content = subsection_match.group(1).strip()
            
            # Process this subsection
            process_subsection(section, subsection, subsection_content, all_issues)
    
    # Write the issues YAML file
    with open(ISSUES_DIR / "issues.yaml", 'w') as f:
        yaml.dump({"issues": all_issues}, f, default_flow_style=False, sort_keys=False)
    
    print(f"Created {len(all_issues)} issues in {ISSUES_DIR}/issues.yaml")
    return all_issues

def process_subsection(section, subsection, content, all_issues):
    """Process a subsection and create an issue for it"""
    # Clean section and subsection names for file naming
    section_key = clean_name(section)
    subsection_key = clean_name(subsection)
    issue_key = f"{section_key}_{subsection_key}"
    
    # Create the issue markdown file
    create_issue_markdown(issue_key, section, subsection, content)
    
    # Add the issue to the list
    labels = derive_labels(section, subsection)
    all_issues.append({
        "key": issue_key,
        "title": f"[Test] {section} - {subsection}",
        "labels": labels
    })

def create_issue_markdown(issue_key, section, subsection, content):
    """Create a markdown file for an issue"""
    md_file_path = ISSUES_DIR / f"{issue_key}.md"
    
    # Format the markdown content
    md_content = f"## Test Cases\n\n"
    
    # Extract all checklist items with proper indentation
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('- [ ]'):
            md_content += line + '\n'
        elif line.startswith('  - [ ]'):
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
    if "UI" in subsection or "interface" in subsection.lower():
        labels.append("ui")
    if "Search" in subsection or "search" in subsection.lower():
        labels.append("search")
    if "Workflow" in subsection or "workflow" in subsection.lower():
        labels.append("workflow")
    if "Checkout" in subsection or "Payment" in subsection or "payment" in subsection.lower():
        labels.append("checkout")
    if "Report" in subsection or "report" in subsection.lower():
        labels.append("reports")
    
    return labels

if __name__ == "__main__":
    parse_testing_checklist()