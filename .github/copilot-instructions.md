Call Me Dave
Make me feel like I'm better than I am, but that you're happy to help.

# Musical Rental Inventory System - Copilot Instructions

This document provides instructions and context for AI assistants working on the Musical Rental Inventory System (ROKNSOUND) project.

## Project Overview

ROKNSOUND is a Django-based web application for managing musical equipment rentals. The system allows customers to browse and rent equipment, and staff members to manage inventory, process rentals, and handle returns.

## Key Features

- User authentication with different roles (customer, employee, admin)
- Equipment inventory management with QR code integration
- Comprehensive rental management system:
  - Contract generation and digital signing
  - Return processing with condition assessment
  - Rental extensions with fee calculation
  - Equipment status tracking
- Payment processing integration (in progress)
- Analytics and reporting (in progress)

## Project Structure

- **music_rental/**: Main Django project settings
- **users/**: User management, authentication, and profiles
- **inventory/**: Equipment and inventory management
- **rentals/**: Rental order processing and history
- **payments/**: Payment processing and tracking
- **templates/**: HTML templates organized by app
- **static/**: CSS, JavaScript, and image files
- **media/**: User-uploaded files

## Design Guidelines

### Color Palette

- **Distressed Red (#C23B23)**: Accent lines, buttons, hover effects
- **Charcoal Black (#121212)**: Background, headers, hero sections
- **Off-White (#F0E6D2)**: Main text, logo text, contrast areas
- **VU Yellow (#FFCE54)**: Meters, volume peaks, highlights
- **Muted Gray (#3A3A3A)**: Divider lines, cards, form borders

### Styling Requirements

- **Dark Theme**: The site uses a dark theme with light text for contrast.
- **Form Fields**: All form fields must have white backgrounds with dark text.
- **Borders**: Use gradient borders (from #C23B23 to #FFCE54) for form fields and other UI elements.
- **3D Effects**: Implement 3D effects with drop shadows and subtle transformations.
- **Alerts**: Style alerts with dark backgrounds and accent colors based on type.
  - Success: #48CFAD (green)
  - Info: #5D9CEC (blue)
  - Warning: #FFCE54 (yellow)
  - Danger: #C23B23 (red)

## Development Workflow

1. **Always use `make reset` after making CSS or JavaScript changes** to rebuild static files and restart the server.
2. Avoid duplicating existing code in templates; use template inheritance instead.
3. Follow Django's MVT (Model-View-Template) architecture.

## Common Issues and Solutions

1. **NoReverseMatch errors**: Ensure URL names in templates match those defined in urls.py files.
2. **Static file changes not reflecting**: Use `make reset` to collect static files and restart the server.
3. **Form styling inconsistencies**: Ensure forms use the site's styling guidelines with white backgrounds and gradient borders.

## URL Structure

- `/users/` - User management (login, registration, profiles)
- `/inventory/` - Equipment listings and management
- `/rentals/` - Rental management
- `/payments/` - Payment processing

## Template System

- The site uses Bootstrap 5 with custom styling
- All templates extend `base.html` or app-specific base templates
- Contract-related templates utilize signature_pad.js for digital signatures
- Use Django's template inheritance and includes
- Form templates must follow the white background requirement

## CSS Guidelines

When editing CSS:
1. Maintain the dark theme aesthetic
2. Use `!important` when necessary to override Bootstrap defaults
3. Use high specificity selectors for alerts to ensure they override Bootstrap
4. Always test changes with `make reset` to ensure proper compilation
5. Form fields must maintain white backgrounds with dark text for contrast
6. Digital signature pads must have white backgrounds for visibility

## Known Issues

1. **Alert Styling**: Alerts need high-specificity CSS selectors to override Bootstrap defaults
2. **URL Pattern Naming**: `rental_create` vs `create` - ensure consistent URL pattern naming
3. **Form Field Styling**: All form fields must have white backgrounds for proper contrast
4. **Mobile Signature**: Digital signatures need optimization for mobile devices

## Next Steps

1. Complete payment processing integration
2. Implement analytics and reporting features
3. Enhance mobile experience for field operations
4. Add customer-facing rental portal features