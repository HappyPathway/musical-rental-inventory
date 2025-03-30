from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Rental, RentalItem, Customer, Contract
from inventory.models import Equipment
from inventory.utils import log_search_query
from .forms import RentalForm, RentalItemForm, RentalReturnForm, RentalExtensionForm, ContractForm
from decimal import Decimal
from datetime import date

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
        'status_filter': status_filter,
        'status_choices': Rental.STATUS_CHOICES,
    }
    
    return render(request, 'rentals/rental_list.html', context)

@login_required
def rental_detail(request, pk):
    """View to display details of a specific rental."""
    rental = get_object_or_404(Rental, pk=pk)
    context = {
        'rental': rental,
        'items': rental.items.all()
    }
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
            return redirect('rentals:rental_detail', pk=rental.id)
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
    
    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rental #{rental.id} updated successfully!')
            return redirect('rentals:rental_detail', pk=rental.id)
    else:
        form = RentalForm(instance=rental)
    
    context = {
        'form': form,
        'rental': rental,
    }
    return render(request, 'rentals/rental_form.html', context)

@login_required
def rental_cancel(request, pk):
    """View to cancel a rental."""
    rental = get_object_or_404(Rental, pk=pk)
    
    if rental.status != 'pending':
        messages.error(request, 'Only pending rentals can be cancelled.')
        return redirect('rentals:rental_detail', pk=rental.id)
    
    if request.method == 'POST':
        rental.status = 'cancelled'
        rental.save()
        
        # Release any equipment back to available status
        for item in rental.items.all():
            equipment = item.equipment
            equipment.status = 'available'
            equipment.save()
        
        messages.success(request, f'Rental #{rental.id} has been cancelled.')
        return redirect('rentals:rental_list')
    
    context = {
        'rental': rental,
    }
    return render(request, 'rentals/rental_cancel.html', context)

@login_required
def rental_return(request, pk):
    """View to handle the return of a rental."""
    rental = get_object_or_404(Rental, pk=pk)
    
    if rental.status not in ['active', 'overdue']:
        messages.error(request, 'Only active or overdue rentals can be returned.')
        return redirect('rentals:rental_detail', pk=pk)
    
    if request.method == 'POST':
        forms = {}
        valid_forms = True
        
        # Process each item in the rental
        for item in rental.items.all():
            form = RentalReturnForm(request.POST, prefix=str(item.id))
            forms[item.id] = form
            if not form.is_valid():
                valid_forms = False
        
        if valid_forms:
            total_late_fees = Decimal('0.00')
            total_damage_fees = Decimal('0.00')
            
            # Process each item's return
            for item in rental.items.all():
                form = forms[item.id]
                
                # Update item condition and return status
                item.condition_note_return = form.cleaned_data['condition_notes']
                item.returned = True
                item.returned_date = timezone.now()
                item.save()
                
                # Update equipment status based on condition
                equipment = item.equipment
                if form.cleaned_data['condition'] in ['poor', 'damaged']:
                    equipment.status = 'maintenance'
                else:
                    equipment.status = 'available'
                equipment.save()
                
                # Accumulate fees
                total_late_fees += form.cleaned_data['late_fees']
                total_damage_fees += form.cleaned_data['damage_fees']
            
            # Update rental status
            rental.status = 'completed'
            rental.save()
            
            messages.success(
                request,
                f'Rental #{rental.id} has been returned successfully. '
                f'Late fees: ${total_late_fees}, Damage fees: ${total_damage_fees}'
            )
            return redirect('rentals:rental_list')
    else:
        # Create a form for each rental item
        forms = {
            item.id: RentalReturnForm(prefix=str(item.id))
            for item in rental.items.all()
        }
        
        # Calculate any late fees
        if rental.end_date < date.today():
            days_late = (date.today() - rental.end_date).days
            for item_id in forms:
                forms[item_id].initial['late_fees'] = Decimal(days_late * 10)  # $10 per day late fee
    
    context = {
        'rental': rental,
        'forms': forms,
    }
    return render(request, 'rentals/rental_return.html', context)

@login_required
def rental_extend(request, pk):
    """View to handle rental extensions."""
    rental = get_object_or_404(Rental, pk=pk)
    
    if rental.status not in ['active', 'overdue']:
        messages.error(request, 'Only active or overdue rentals can be extended.')
        return redirect('rentals:rental_detail', pk=pk)
    
    if request.method == 'POST':
        form = RentalExtensionForm(request.POST)
        if form.is_valid():
            new_end_date = form.cleaned_data['new_end_date']
            
            if new_end_date <= rental.end_date:
                messages.error(request, 'New end date must be after current end date.')
                return redirect('rentals:rental_extend', pk=pk)
            
            # Calculate additional charges
            days_extended = (new_end_date - rental.end_date).days
            additional_charge = Decimal(days_extended * 10)  # $10 per day extension fee
            
            # Update rental
            rental.end_date = new_end_date
            rental.total_price += additional_charge
            rental.notes += f"\n[Extension] {form.cleaned_data['extension_notes']}"
            rental.status = 'active'  # Reset to active if it was overdue
            rental.save()
            
            messages.success(
                request,
                f'Rental extended successfully. Additional charge: ${additional_charge}'
            )
            return redirect('rentals:rental_detail', pk=pk)
    else:
        form = RentalExtensionForm(initial={'new_end_date': rental.end_date})
    
    context = {
        'rental': rental,
        'form': form,
    }
    return render(request, 'rentals/rental_extend.html', context)

@login_required
def rental_sign(request, pk):
    """View to sign a rental contract."""
    rental = get_object_or_404(Rental, pk=pk)
    
    # Don't allow signing if already signed
    if rental.contract_signed:
        messages.info(request, 'This rental contract has already been signed.')
        return redirect('rentals:rental_detail', pk=pk)
    
    # Only allow signing pending rentals
    if rental.status != 'pending':
        messages.error(request, 'Only pending rentals can be signed.')
        return redirect('rentals:rental_detail', pk=pk)
    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            # Update rental with signature data
            rental.contract_signed = True
            rental.contract_signed_date = timezone.now()
            rental.contract_signature_data = form.cleaned_data['signature']
            rental.status = 'active'  # Activate the rental
            rental.save()
            
            # Update equipment status
            for item in rental.items.all():
                equipment = item.equipment
                equipment.status = 'rented'
                equipment.save()
            
            messages.success(request, 'Contract signed successfully! Your rental is now active.')
            return redirect('rentals:rental_detail', pk=pk)
    else:
        form = ContractForm()
    
    try:
        contract = rental.contract
    except Contract.DoesNotExist:
        messages.error(request, 'No contract found for this rental.')
        return redirect('rentals:rental_detail', pk=pk)
    
    context = {
        'rental': rental,
        'contract': contract,
        'form': form,
    }
    return render(request, 'rentals/rental_sign.html', context)
