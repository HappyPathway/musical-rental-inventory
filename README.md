# ROKNSOUND Musical Rental Inventory System

A powerful Django-based web application for managing musical equipment rentals with a distinctive dark theme aesthetic.

## Administrator Guide: Managing & Renting Inventory

This guide will walk administrators through the essential processes of managing inventory and processing rentals in the ROKNSOUND system.

### 1. Accessing Admin Features

As an administrator, you have full access to all features of the ROKNSOUND system. 

#### Login & Dashboard Access

1. **Login**: Navigate to `http://localhost:8000/users/login/` and enter your admin credentials
2. **Admin Dashboard**: After login, you'll be redirected to the staff dashboard
3. **Admin Interface**: Access the Django admin at `http://localhost:8000/admin/` for advanced database operations

The staff dashboard provides quick access to all key functions. Admins see additional management options in the "Admin Functions" section.

### 2. Inventory Management

#### Adding New Equipment

1. From the staff dashboard, click the "Add Equipment" card
2. Complete the equipment form with these essential details:
   - **Name**: Clear, descriptive title for the equipment
   - **Category**: Select from existing or create new categories
   - **Brand & Model**: Manufacturer information
   - **Pricing**: Set daily, weekly, and monthly rates
   - **Deposit Amount**: Security deposit required
   - **Images**: Upload high-quality photos (main image is required)
   - **Description**: Detailed specifications and features
   - **Serial Number**: Unique identifier for the specific item

3. Click "Save" to create the inventory item

The system automatically generates QR codes for each equipment item that can be scanned for quick access to equipment details.

#### Managing Existing Equipment

1. **View All Equipment**: Navigate to "View Inventory" to see all items
2. **Filtering**: Use category and status filters to find specific items
3. **Search**: Use the search box to find equipment by name, brand, or serial number
4. **Edit Equipment**: Click on any item, then the "Edit Equipment" button
5. **Delete Equipment**: From the equipment detail page, use the "Delete Equipment" button

#### Equipment Status Management

Equipment can have the following statuses:
- **Available**: Ready to be rented
- **Rented**: Currently on loan to a customer
- **Maintenance**: Temporarily unavailable due to repairs
- **Damaged**: Requires assessment or repair
- **Retired**: No longer in circulation

To change an equipment's status:
1. Navigate to the equipment detail page
2. Click "Edit Equipment"
3. Update the status field
4. Save changes

#### Maintenance Records

Track equipment maintenance:
1. From equipment detail page, scroll to "Maintenance History"
2. Click "Add Maintenance Record"
3. Enter maintenance details and costs
4. Optionally update equipment status to "Maintenance"

### 3. Rental Management

#### Creating New Rentals

1. From the staff dashboard, click "View Rentals" then "Create Rental"
2. Select a customer (or create a new one)
3. Add equipment items to the rental:
   - Search for equipment by name/serial number
   - Verify availability status
   - Specify rental period (daily, weekly, monthly)
4. Review rental details and total costs
5. Generate and sign rental contract
6. Collect security deposit
7. Finalize the rental

#### Contract Management

1. **Contract Generation**
   - Automatically generated when creating a rental
   - Contains equipment details, pricing, and rental terms
   - Lists all equipment with serial numbers
   - Shows deposit amounts and fees

2. **Digital Signing Process**
   - Review contract terms
   - Use digital signature pad (mouse or touch input)
   - Check agreement checkbox
   - Contract is timestamped upon signing

3. **Post-Signing Actions**
   - Rental status changes to 'active'
   - Equipment status updates to 'rented'
   - Contract becomes part of rental record
   - Digital signature stored securely

#### Processing Returns

1. From "View Rentals", find the active rental
2. Click on the rental ID to view details
3. Click "Process Return"
4. For each equipment item:
   - Assess condition and note any damage
   - Calculate applicable fees:
     - Late return charges ($10/day)
     - Damage fees if applicable
     - Missing accessories charges
5. Process payment or refund deposit
6. Complete return to update inventory

#### Managing Rental Extensions

1. From the rental detail page, click "Extend Rental"
2. Select new return date
3. Calculate additional charges:
   - Extension fees ($10/day)
   - Any overdue fees if applicable
4. Process additional payment
5. Update rental record

### 4. User Management

#### Customer Management

1. View all customers: From Admin Functions → "Manage Users"
2. Create new customer account: Users → Register
3. Edit customer details: Click on user name → Edit Profile
4. View customer rental history: Click on username → View Rentals

#### Staff Management

1. Add staff member: Admin Functions → "Add Staff Member"
2. Set staff permissions: When creating account or through "Change User Type"
3. View staff activity: Admin Functions → Activity Logs

### 5. Reports & Analytics

Access key business metrics:
1. Navigate to Admin Dashboard
2. View rental statistics in the dashboard widgets
3. For detailed reports, use the Django Admin interface

### 6. Search Tracking

The system tracks all search queries to help improve inventory management:
1. Access search logs through the Django Admin interface
2. View popular search terms to identify equipment demand
3. Track zero-result searches to identify inventory gaps

### Troubleshooting Common Issues

1. **Payment Processing Errors**: Verify payment integration settings in admin panel
2. **QR Code Scanning Issues**: Ensure good lighting and camera access
3. **Inventory Discrepancies**: Run inventory audit report from admin panel

## Development Setup

For information on setting up the development environment, please see the [Development Guide](DEVELOPMENT.md).

## License

Copyright © 2025 ROKNSOUND LLC.