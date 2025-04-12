from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Rental, RentalItem, Customer
from .forms import RentalForm, RentalItemForm, CustomerForm, ReturnRentalItemForm, ContractSignatureForm, StaffRentalForm, StaffRentalItemForm
from inventory.models import Equipment
from inventory.utils import log_search_query
from decimal import Decimal

# Rental list and detail views remain unchanged

@login_required
def rental_list(request):
    """View to display a list of all rentals."""
    # Get search and filter parameters
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    # Determine if user is staff
    is_staff = request.user.is_staff or request.user.is_superuser
    
    # Start with all rentals for staff, or just user's rentals for normal users
    if is_staff:
        rentals_list = Rental.objects.all().order_by('-start_date')
    else:
        # For regular users, show only their own rentals
        try:
            customer = Customer.objects.get(user=request.user)
            rentals_list = Rental.objects.filter(customer=customer).order_by('-start_date')
        except Customer.DoesNotExist:
            rentals_list = Rental.objects.none()
    
    # Apply status filter if provided
    if status_filter:
        rentals_list = rentals_list.filter(status=status_filter)
    
    # Apply search filter if provided
    if search_query:
        rentals_list = rentals_list.filter(
            Q(customer__first_name__icontains=search_query) | 
            Q(customer__last_name__icontains=search_query) | 
            Q(customer__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
        
        # Log the search query
        log_search_query(
            request=request,
            query=search_query,
            app='rentals',
            results_count=rentals_list.count()
        )
    
    # Pagination
    paginator = Paginator(rentals_list, 10)  # Show 10 rentals per page
    page = request.GET.get('page')
    rentals = paginator.get_page(page)
    
    context = {
        'rentals': rentals,
        'rental_list': rentals_list,  # Add the unfiltered list for tests
        'search_query': search_query,
        'status_filter': status_filter,
        'is_staff': is_staff
    }
    
    return render(request, 'rentals/rental_list.html', context)

@login_required
def rental_detail(request, pk):
    """View to display details of a specific rental."""
    rental = get_object_or_404(Rental, pk=pk)
    
    # Check if the user is authorized to view this rental
    is_staff = request.user.is_staff or request.user.is_superuser
    is_owner = hasattr(request.user, 'customer') and request.user.customer == rental.customer
    
    if not (is_staff or is_owner):
        messages.error(request, "You don't have permission to view this rental.")
        return redirect('rentals:rental_list')
    
    context = {
        'rental': rental,
        'is_staff': is_staff
    }
    return render(request, 'rentals/rental_detail.html', context)

@login_required
def rental_create(request):
    """View to create a new rental."""
    # Check if there's an equipment ID in the query parameters
    equipment_id = request.GET.get('equipment')
    
    # Determine if user is staff or admin
    is_staff = request.user.is_staff or request.user.is_superuser
    
    if request.method == 'POST':
        # Use different forms for staff vs regular users
        if is_staff:
            form = StaffRentalForm(request.POST)
        else:
            form = RentalForm(request.POST)
            
        if form.is_valid():
            rental = form.save(commit=False)
            
            # For non-staff users, automatically set the customer to their own customer record
            if not is_staff:
                try:
                    # Try to get the customer record linked to the user
                    rental.customer = Customer.objects.get(user=request.user)
                except Customer.DoesNotExist:
                    messages.error(request, "You don't have a customer profile. Please contact the staff.")
                    return redirect('home')  # Changed from 'index' to 'home'
            
            # Set initial values for price fields
            rental.total_price = Decimal('0.00')
            rental.deposit_total = Decimal('0.00')
            
            rental.save()
            messages.success(request, f'Rental created! Now add equipment items.')
            
            # If we have an equipment ID from query params, redirect to add_rental_item with that equipment pre-selected
            if equipment_id:
                return redirect(f'/rentals/{rental.id}/add-item/?equipment={equipment_id}')
            else:
                return redirect('rentals:add_rental_item', pk=rental.id)
    else:
        # Use different forms for staff vs regular users
        if is_staff:
            form = StaffRentalForm()
        else:
            form = RentalForm()
    
    # Pass the equipment_id to the template context
    context = {
        'form': form, 
        'title': 'Create New Rental',
        'equipment_id': equipment_id,
        'is_staff': is_staff
    }
    return render(request, 'rentals/rental_form.html', context)

@login_required
def add_rental_item(request, pk):
    """Add equipment items to a rental."""
    rental = get_object_or_404(Rental, pk=pk)
    
    # Check if equipment ID is passed in query parameters
    equipment_id = request.GET.get('equipment')
    
    # Determine if user is staff or admin
    is_staff = request.user.is_staff or request.user.is_superuser
    
    if request.method == 'POST':
        # Use different forms for staff vs regular users
        if is_staff:
            form = StaffRentalItemForm(request.POST)
        else:
            form = RentalItemForm(request.POST)
            
        if form.is_valid():
            rental_item = form.save(commit=False)
            rental_item.rental = rental
            
            # Get equipment and calculate price based on duration type and quantity
            equipment = form.cleaned_data['equipment']
            quantity = form.cleaned_data['quantity']
            
            if rental.duration_type == 'daily':
                price_per_unit = equipment.rental_price_daily
            elif rental.duration_type == 'weekly':
                price_per_unit = equipment.rental_price_weekly
            else:  # monthly
                price_per_unit = equipment.rental_price_monthly
                
            # Set the price for this item (price per unit * quantity)
            # For staff users, use the price and condition notes from the form if provided
            if is_staff and 'price' in form.cleaned_data:
                rental_item.price = form.cleaned_data['price']
                if 'condition_note_checkout' in form.cleaned_data:
                    rental_item.condition_note_checkout = form.cleaned_data['condition_note_checkout']
            else:
                rental_item.price = price_per_unit * quantity
                rental_item.condition_note_checkout = ''  # Empty for regular users
            
            rental_item.save()
            
            # Update rental totals
            rental.total_price = rental.calculate_total_price()
            rental.deposit_total = rental.calculate_deposit_total()
            rental.save()
            
            messages.success(request, f'Added {quantity}x {equipment.name} to the rental.')
            
            # If "add another" was clicked, redirect back to the same form
            if 'add_another' in request.POST:
                return redirect('rentals:add_rental_item', pk=rental.id)
            else:
                return redirect('rentals:rental_detail', pk=rental.id)
    else:
        # Pre-select equipment if ID was provided in query params
        initial_data = {}
        if equipment_id:
            try:
                equipment = Equipment.objects.get(pk=equipment_id)
                initial_data = {'equipment': equipment}
                
                # For staff users, also pre-calculate and set the default price
                if is_staff:
                    if rental.duration_type == 'daily':
                        initial_data['price'] = equipment.rental_price_daily
                    elif rental.duration_type == 'weekly':
                        initial_data['price'] = equipment.rental_price_weekly
                    else:  # monthly
                        initial_data['price'] = equipment.rental_price_monthly
                        
            except Equipment.DoesNotExist:
                pass
        
        # Use different forms for staff vs regular users
        if is_staff:
            form = StaffRentalItemForm(initial=initial_data)
        else:
            form = RentalItemForm(initial=initial_data)
    
    # Get current items for display
    rental_items = rental.items.all()
    
    context = {
        'rental': rental,
        'form': form,
        'rental_items': rental_items,
        'title': f'Add Equipment to Rental #{rental.id}',
        'is_staff': is_staff
    }
    return render(request, 'rentals/add_rental_item.html', context)

@login_required
def remove_rental_item(request, rental_pk, item_pk):
    """Remove an item from a rental."""
    rental = get_object_or_404(Rental, pk=rental_pk)
    item = get_object_or_404(RentalItem, pk=item_pk, rental=rental)
    
    if request.method == 'POST':
        # Update equipment status back to available
        equipment = item.equipment
        equipment.status = 'available'
        equipment.save()
        
        # Delete the item
        item.delete()
        
        # Update rental totals
        rental.total_price = rental.calculate_total_price()
        rental.deposit_total = rental.calculate_deposit_total()
        rental.save()
        
        messages.success(request, f'Removed {item.equipment.name} from the rental.')
    
    return redirect('rentals:add_rental_item', pk=rental.pk)

@login_required
def rental_return(request, pk):
    """View to handle the return of a rental."""
    rental = get_object_or_404(Rental, pk=pk)

    if request.method == 'POST':
        # Inspect returned equipment
        for item in rental.items.all():
            item.returned = True
            item.returned_date = timezone.now()
            item.save()

            # Update equipment status to available
            equipment = item.equipment
            equipment.status = 'available'
            equipment.save()

        # Calculate late fees if applicable
        if rental.is_overdue():
            overdue_days = (timezone.now().date() - rental.end_date).days
            late_fee = overdue_days * Decimal('10.00')  # Example late fee per day
            rental.total_price += late_fee
            messages.warning(request, f'Late fee of ${late_fee:.2f} applied for {overdue_days} overdue days.')

        # Mark rental as completed
        rental.mark_as_returned()
        messages.success(request, f'Rental #{rental.id} has been successfully returned.')

        return redirect('rentals:rental_detail', pk=rental.id)

    context = {'rental': rental}
    return render(request, 'rentals/rental_return.html', context)

@login_required
def rental_cancel(request, pk):
    """View to cancel a rental."""
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == 'POST':
        rental.status = 'cancelled'
        rental.save()
        messages.success(request, f'Rental #{rental.id} has been cancelled.')
        return redirect('rentals:rental_list')
    # Placeholder implementation for GET request
    context = {'rental': rental}
    return render(request, 'rentals/rental_cancel.html', context)

@login_required
def rental_contract(request, pk):
    """View to generate a rental contract."""
    rental = get_object_or_404(Rental, pk=pk)
    # Placeholder implementation
    context = {'rental': rental}
    return render(request, 'rentals/rental_contract.html', context)

@login_required
def rental_sign(request, pk):
    """View to handle signing a rental contract."""
    rental = get_object_or_404(Rental, pk=pk)
    # Placeholder implementation
    context = {'rental': rental}
    return render(request, 'rentals/rental_sign.html', context)

@login_required
def rental_edit(request, pk):
    """View to edit an existing rental."""
    rental = get_object_or_404(Rental, pk=pk)
    
    # Check if the user is authorized to edit this rental
    is_staff = request.user.is_staff or request.user.is_superuser
    is_owner = hasattr(request.user, 'customer') and request.user.customer == rental.customer
    
    if not (is_staff or is_owner):
        messages.error(request, "You don't have permission to edit this rental.")
        return redirect('rentals:rental_list')
    
    if request.method == 'POST':
        # Use different forms for staff vs regular users
        if is_staff:
            form = StaffRentalForm(request.POST, instance=rental)
        else:
            form = RentalForm(request.POST, instance=rental)
            
        if form.is_valid():
            form.save()
            messages.success(request, f'Rental #{rental.id} has been updated.')
            return redirect('rentals:rental_detail', pk=rental.id)
    else:
        # Use different forms for staff vs regular users
        if is_staff:
            form = StaffRentalForm(instance=rental)
        else:
            form = RentalForm(instance=rental)
    
    context = {
        'form': form,
        'rental': rental,
        'title': f'Edit Rental #{rental.id}',
        'is_staff': is_staff
    }
    return render(request, 'rentals/rental_form.html', context)
