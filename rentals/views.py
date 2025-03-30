from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Rental, RentalItem
from inventory.models import Equipment
from inventory.utils import log_search_query
from .forms import RentalForm, RentalItemForm

# Placeholder views for the rental app
# These will be implemented more fully later

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
        rental_form = RentalForm(request.POST)
        rental_item_form = RentalItemForm(request.POST)

        if rental_form.is_valid() and rental_item_form.is_valid():
            # Save the rental
            rental = rental_form.save(commit=False)
            rental.total_price = 0  # Initialize total price
            rental.deposit_total = 0  # Initialize deposit total
            rental.save()

            # Save the rental item
            equipment = rental_item_form.cleaned_data['equipment']
            price = rental_item_form.cleaned_data['price']
            RentalItem.objects.create(rental=rental, equipment=equipment, price=price)

            # Update rental totals
            rental.total_price = rental.calculate_total_price()
            rental.deposit_total = rental.calculate_deposit_total()
            rental.save()

            messages.success(request, f'Rental #{rental.id} created successfully!')
            return redirect('rentals:rental_list')
    else:
        rental_form = RentalForm()
        rental_item_form = RentalItemForm()

    context = {
        'rental_form': rental_form,
        'rental_item_form': rental_item_form,
    }
    return render(request, 'rentals/rental_form.html', context)

@login_required
def rental_edit(request, pk):
    """View to edit an existing rental."""
    rental = get_object_or_404(Rental, pk=pk)
    # Placeholder implementation
    context = {'rental': rental}
    return render(request, 'rentals/rental_form.html', context)

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
