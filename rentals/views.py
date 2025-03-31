from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Rental, RentalItem, Customer
from .forms import RentalForm, RentalItemForm, CustomerForm, ReturnRentalItemForm, ContractSignatureForm
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
    
    # Start with all rentals
    rentals_list = Rental.objects.all().order_by('-start_date')
    
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
        'search_query': search_query,
        'status_filter': status_filter
    }
    
    return render(request, 'rentals/rental_list.html', context)

@login_required
def rental_detail(request, pk):
    """View to display details of a specific rental."""
    rental = get_object_or_404(Rental, pk=pk)
    context = {'rental': rental}
    # Use a placeholder template for now
    return render(request, 'rentals/rental_detail.html', context)

@login_required
def rental_create(request):
    """View to create a new rental."""
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            
            # Set initial values for price fields
            rental.total_price = Decimal('0.00')
            rental.deposit_total = Decimal('0.00')
            
            rental.save()
            messages.success(request, f'Rental created! Now add equipment items.')
            return redirect('rentals:add_rental_item', pk=rental.id)
    else:
        form = RentalForm()
    
    context = {'form': form, 'title': 'Create New Rental'}
    return render(request, 'rentals/rental_form.html', context)

@login_required
def add_rental_item(request, pk):
    """Add equipment items to a rental."""
    rental = get_object_or_404(Rental, pk=pk)
    
    if request.method == 'POST':
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
            rental_item.price = price_per_unit * quantity
            
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
        form = RentalItemForm()
    
    # Get current items for display
    rental_items = rental.items.all()
    
    context = {
        'rental': rental,
        'form': form,
        'rental_items': rental_items,
        'title': f'Add Equipment to Rental #{rental.id}'
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
    # Placeholder implementation
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
    
    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rental #{rental.id} has been updated.')
            return redirect('rentals:rental_detail', pk=rental.id)
    else:
        form = RentalForm(instance=rental)
    
    context = {
        'form': form,
        'rental': rental,
        'title': f'Edit Rental #{rental.id}'
    }
    return render(request, 'rentals/rental_form.html', context)
