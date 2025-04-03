# Authentication Testing Issues
resource "github_issue" "auth_registration" {
  repository = "musical-rental-inventory"
  title      = "[Test] Authentication - User Registration"
  body       = <<-EOT
## Test Cases
- [ ] Access registration page from home page
- [ ] Access registration page from login page
- [ ] Attempt registration with missing required fields
- [ ] Attempt registration with invalid email format
- [ ] Attempt registration with mismatched passwords
- [ ] Attempt registration with too short password
- [ ] Successfully register new customer account with valid data
- [ ] Verify redirect to dashboard after registration
- [ ] Verify welcome email received

## Notes
- Document any failures or unexpected behavior
- Note any browser-specific issues
- Track completion status
EOT
  labels     = ["testing", "authentication"]
}

resource "github_issue" "auth_login" {
  repository = "musical-rental-inventory"
  title      = "[Test] Authentication - Login System"
  body       = <<-EOT
## Test Cases
- [ ] Access login page from home page
- [ ] Access login page from navigation
- [ ] Attempt login with invalid credentials
- [ ] Attempt login with empty fields
- [ ] Successfully login as customer
- [ ] Successfully login as staff
- [ ] Successfully login as admin
- [ ] Verify redirect to originally requested page after login

### Password Reset Flow
- [ ] Request password reset
- [ ] Verify reset email received
- [ ] Reset password using link
- [ ] Login with new password

## Notes
- Document any failures or unexpected behavior
- Test with different user roles
- Verify email notifications
EOT
  labels     = ["testing", "authentication"]
}

# Equipment Testing Issues
resource "github_issue" "equipment_listing" {
  repository = "musical-rental-inventory"
  title      = "[Test] Equipment - Listing Views"
  body       = <<-EOT
## Test Cases

### View Access
- [ ] View equipment list as unauthenticated user
- [ ] View equipment list as customer
- [ ] View equipment list as staff

### Filtering & Search
- [ ] Verify status filter only shows for staff
- [ ] Test category filter functionality
- [ ] Test search by name
- [ ] Test search by description
- [ ] Test search by brand
- [ ] Test search by serial number

### UI Features
- [ ] Verify pagination works
- [ ] Test sort by name
- [ ] Test sort by category
- [ ] Test sort by availability

## Notes
- Test with various screen sizes
- Verify filter combinations work
- Check search performance with large datasets
EOT
  labels     = ["testing", "equipment"]
}

resource "github_issue" "equipment_management" {
  repository = "musical-rental-inventory"
  title      = "[Test] Equipment - Staff Management"
  body       = <<-EOT
## Test Cases

### Adding Equipment
- [ ] Add equipment with minimum required fields
- [ ] Add equipment with all fields
- [ ] Add equipment with multiple images
- [ ] Verify validation rules

### Editing Equipment
- [ ] Update basic information
- [ ] Update status
- [ ] Update pricing
- [ ] Add/remove images
- [ ] Test validation rules

### Deleting Equipment
- [ ] Verify confirmation dialog
- [ ] Test deletion with no rental history
- [ ] Test deletion with rental history
- [ ] Verify related records are handled properly

## Notes
- Test image upload limits
- Verify audit trail logging
- Check permission requirements
EOT
  labels     = ["testing", "equipment", "management"]
}

# Rental Testing Issues
resource "github_issue" "rental_creation" {
  repository = "musical-rental-inventory"
  title      = "[Test] Rentals - Creation Process"
  body       = <<-EOT
## Test Cases

### Access Control
- [ ] Attempt rental as unauthenticated user (should redirect to login)
- [ ] Create rental as customer
- [ ] Create rental as staff for customer

### Rental Options
- [ ] Create single item rental
- [ ] Create multiple item rental
- [ ] Test different date ranges

### Validation
- [ ] Test past dates (should fail)
- [ ] Test invalid date ranges
- [ ] Test overlapping rentals
- [ ] Verify pricing calculation
- [ ] Test equipment availability checking

## Notes
- Test with various equipment combinations
- Verify price calculations
- Check availability conflicts
EOT
  labels     = ["testing", "rentals"]
}

resource "github_issue" "rental_workflow" {
  repository = "musical-rental-inventory"
  title      = "[Test] Rentals - Workflow Process"
  body       = <<-EOT
## Test Cases

### Initial Process
- [ ] Submit rental request
- [ ] Verify confirmation email
- [ ] Test staff approval process
- [ ] Verify payment processing

### Equipment Handling
- [ ] Test equipment pickup process
- [ ] Test equipment return process
- [ ] Test damage reporting
- [ ] Verify late return handling

### Status Updates
- [ ] Verify status changes are logged
- [ ] Test notification system
- [ ] Verify customer notifications
- [ ] Test staff notifications

## Notes
- Test complete workflow end-to-end
- Verify all notifications
- Check status transitions
EOT
  labels     = ["testing", "rentals", "workflow"]
}
