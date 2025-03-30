from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Equipment, Category, EquipmentAttachment, MaintenanceRecord
from .forms import EquipmentForm, AttachmentForm, MaintenanceRecordForm
from .utils import log_search_query
import qrcode
from io import BytesIO
import base64
import json

def equipment_list(request):
    """Display a list of equipment with filtering options."""
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search_query = request.GET.get('search', '')
    
    # Start with all equipment
    equipment_list = Equipment.objects.all()
    
    # Apply filters
    if category_id:
        equipment_list = equipment_list.filter(category_id=category_id)
    
    if status:
        equipment_list = equipment_list.filter(status=status)
    
    if search_query:
        equipment_list = equipment_list.filter(
            name__icontains=search_query
        ) | equipment_list.filter(
            description__icontains=search_query
        ) | equipment_list.filter(
            brand__icontains=search_query
        ) | equipment_list.filter(
            serial_number__icontains=search_query
        )
        
        # Log the search query
        log_search_query(
            request=request, 
            query=search_query, 
            app='inventory', 
            results_count=equipment_list.count()
        )
    
    # Pagination
    paginator = Paginator(equipment_list, 12)  # Show 12 items per page
    page = request.GET.get('page')
    equipment = paginator.get_page(page)
    
    # Get all categories for the filter dropdown
    categories = Category.objects.all()
    
    context = {
        'equipment': equipment,
        'categories': categories,
        'category_id': category_id,
        'status': status,
        'search_query': search_query,
        'status_choices': Equipment.STATUS_CHOICES,
    }
    
    return render(request, 'inventory/equipment_list.html', context)

def equipment_detail(request, pk):
    """Display detailed information about a specific equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    attachments = equipment.attachments.all()
    maintenance_records = equipment.maintenance_records.all().order_by('-date')
    
    context = {
        'equipment': equipment,
        'attachments': attachments,
        'maintenance_records': maintenance_records,
    }
    
    return render(request, 'inventory/equipment_detail.html', context)

@login_required
def equipment_add(request):
    """Add a new equipment item."""
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save()
            
            # Handle attachments
            files = request.FILES.getlist('attachments')
            for f in files:
                EquipmentAttachment.objects.create(equipment=equipment, file=f)
            
            messages.success(request, f'Equipment "{equipment.name}" has been added successfully.')
            return redirect('inventory:detail', pk=equipment.pk)
    else:
        form = EquipmentForm()
    
    context = {
        'form': form,
        'title': 'Add New Equipment',
        'is_mobile': is_mobile_device(request),
    }
    
    return render(request, 'inventory/equipment_form.html', context)

@login_required
def equipment_edit(request, pk):
    """Edit an existing equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            equipment = form.save()
            
            # Handle attachments
            files = request.FILES.getlist('attachments')
            for f in files:
                EquipmentAttachment.objects.create(equipment=equipment, file=f)
            
            messages.success(request, f'Equipment "{equipment.name}" has been updated successfully.')
            return redirect('inventory:detail', pk=equipment.pk)
    else:
        form = EquipmentForm(instance=equipment)
    
    context = {
        'form': form,
        'equipment': equipment,
        'title': 'Edit Equipment',
        'is_mobile': is_mobile_device(request),
    }
    
    return render(request, 'inventory/equipment_form.html', context)

@login_required
def equipment_delete(request, pk):
    """Delete an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        equipment_name = equipment.name
        equipment.delete()
        messages.success(request, f'Equipment "{equipment_name}" has been deleted.')
        return redirect('inventory:list')
    
    context = {
        'equipment': equipment,
    }
    
    return render(request, 'inventory/equipment_confirm_delete.html', context)

@login_required
def equipment_qr(request, pk):
    """Generate and display a QR code for an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # If the equipment already has a QR code, use it
    if equipment.qr_code:
        qr_image_url = equipment.qr_code.url
        context = {
            'equipment': equipment,
            'qr_image_url': qr_image_url,
        }
        return render(request, 'inventory/equipment_qr.html', context)
    
    # Otherwise, generate a new QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # QR code will link to the equipment detail page
    url = request.build_absolute_uri(reverse('inventory:detail', args=[equipment.pk]))
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Create base64 encoded string for the template
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'equipment': equipment,
        'qr_image_base64': qr_image_base64,
    }
    
    return render(request, 'inventory/equipment_qr.html', context)

def equipment_scan(request):
    """Handle QR code scanning from mobile devices."""
    context = {
        'is_mobile': is_mobile_device(request),
    }
    return render(request, 'inventory/equipment_scan.html', context)

@login_required
def equipment_scan_result(request):
    """Process the scanned QR code and redirect to the appropriate equipment."""
    if request.method == 'POST':
        data = json.loads(request.body)
        scanned_url = data.get('scanned_url', '')
        
        # Extract the equipment ID from the URL
        # This is just a simple implementation, you might need to make it more robust
        try:
            # Assuming URLs are in format "/inventory/123/"
            parts = scanned_url.split('/')
            equipment_id = next((p for p in parts if p.isdigit()), None)
            
            if equipment_id:
                return JsonResponse({'redirect_url': reverse('inventory:detail', args=[equipment_id])})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_maintenance_record(request, pk):
    """Add a maintenance record to an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance_record = form.save(commit=False)
            maintenance_record.equipment = equipment
            maintenance_record.save()
            
            messages.success(request, 'Maintenance record added successfully.')
            
            # Update equipment status if needed
            if request.POST.get('update_status') == 'on':
                equipment.status = 'maintenance'
                equipment.save()
            
            return redirect('inventory:detail', pk=equipment.pk)
    else:
        form = MaintenanceRecordForm()
    
    context = {
        'form': form,
        'equipment': equipment,
    }
    
    return render(request, 'inventory/maintenance_form.html', context)

@login_required
def add_attachment(request, pk):
    """Add an attachment to an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.equipment = equipment
            attachment.save()
            
            messages.success(request, 'Attachment added successfully.')
            return redirect('inventory:detail', pk=equipment.pk)
    else:
        form = AttachmentForm()
    
    context = {
        'form': form,
        'equipment': equipment,
    }
    
    return render(request, 'inventory/attachment_form.html', context)

def is_mobile_device(request):
    """Detect if the request is coming from a mobile device."""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_agents = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
    return any(agent in user_agent for agent in mobile_agents)
