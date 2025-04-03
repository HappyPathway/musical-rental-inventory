from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Equipment, Category, EquipmentAttachment, MaintenanceRecord
from .forms import EquipmentForm, AttachmentForm, MaintenanceRecordForm
from .utils import log_search_query
import qrcode
from io import BytesIO
import base64
import json
import re

def is_mobile_device(request):
    """
    Enhanced mobile device detection.
    Returns True if the request comes from a mobile device, False otherwise.
    """
    if not request or not request.META.get('HTTP_USER_AGENT'):
        return False

    user_agent = request.META['HTTP_USER_AGENT'].lower()
    
    # Comprehensive list of mobile identifiers
    mobile_patterns = [
        'mobile', 'android', 'iphone', 'ipad', 'ipod', 
        'blackberry', 'windows phone', 'webos', 'opera mini',
        'opera mobi', 'palm', 'symbian', 'nokia', 'samsung',
        'lg', 'htc', 'mot', 'fennec', 'netfront', 'webos',
        'bolt', 'teashark', 'blazer', 'safari mobile', 'webkit mobile',
        'chrome mobile', 'firefox mobile', 'iemobile'
    ]
    
    # Check if the user explicitly requested desktop version
    if request.GET.get('desktop') == '1':
        return False
        
    # Check if the user explicitly requested mobile version
    if request.GET.get('mobile') == '1':
        return True
    
    # Check for common mobile headers
    if request.META.get('HTTP_X_WAP_PROFILE') or \
       request.META.get('HTTP_PROFILE') or \
       request.META.get('X_OPERAMINI_PHONE_UA'):
        return True
        
    # Check accept header for wap.wml or wap.xhtml support
    if request.META.get('HTTP_ACCEPT') and \
       ('application/vnd.wap.xhtml+xml' in request.META['HTTP_ACCEPT'].lower() or \
        'text/vnd.wap.wml' in request.META['HTTP_ACCEPT'].lower()):
        return True
    
    # Check for any mobile pattern in user agent
    return any(pattern in user_agent for pattern in mobile_patterns)

def equipment_list(request):
    """Display a list of equipment with filtering options."""
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search_query = request.GET.get('search', '')
    
    # Start with all equipment
    equipment_list = Equipment.objects.all()
    
    # For non-staff users, always show all equipment regardless of status
    if not request.user.is_staff:
        # Apply category filter if provided
        if category_id:
            equipment_list = equipment_list.filter(category_id=category_id)
    else:
        # Staff users can filter by both category and status
        if category_id:
            equipment_list = equipment_list.filter(category_id=category_id)
        if status:
            equipment_list = equipment_list.filter(status=status)
    
    # Apply search filter
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
    
    # Determine if the request is from a mobile device
    is_mobile = is_mobile_device(request)
    
    context = {
        'equipment': equipment,
        'equipment_list': equipment_list,  # Add the unfiltered list for tests
        'categories': categories,
        'category_id': category_id,
        'status': status,
        'search_query': search_query,
        'status_choices': Equipment.STATUS_CHOICES if request.user.is_staff else None,  # Only pass status choices to staff
        'is_mobile': is_mobile,
    }
    
    # Use mobile template if on mobile device
    template = 'inventory/mobile/equipment_list.html' if is_mobile else 'inventory/equipment_list.html'
    
    return render(request, template, context)

def equipment_detail(request, pk):
    """Display detailed information about a specific equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    attachments = equipment.attachments.all()
    maintenance_records = equipment.maintenance_records.all().order_by('-date')
    
    context = {
        'equipment': equipment,
        'attachments': attachments,
        'maintenance_records': maintenance_records,
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/equipment_detail.html' if is_mobile_device(request) else 'inventory/equipment_detail.html'
    return render(request, template, context)

@login_required
def equipment_add(request):
    """Add a new equipment item."""
    is_mobile = is_mobile_device(request)
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save()
            
            # Handle attachments
            files = request.FILES.getlist('attachments')
            for f in files:
                EquipmentAttachment.objects.create(equipment=equipment, file=f)
            
            messages.success(request, f'Equipment "{equipment.name}" has been added successfully.')
            return redirect('inventory:equipment_detail', pk=equipment.pk)
    else:
        form = EquipmentForm()
    
    context = {
        'form': form,
        'title': 'Add New Equipment',
        'is_mobile': is_mobile,
    }
    
    template = 'inventory/mobile/equipment_form.html' if is_mobile else 'inventory/equipment_form.html'
    return render(request, template, context)

@login_required
def equipment_edit(request, pk):
    """Edit an existing equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        print(f"Form data: {request.POST}")  # Debug
        if form.is_valid():
            print("Form is valid")  # Debug
            equipment = form.save()
            
            # Handle attachments
            files = request.FILES.getlist('attachments')
            for f in files:
                EquipmentAttachment.objects.create(equipment=equipment, file=f)
            
            messages.success(request, f'Equipment "{equipment.name}" has been updated successfully.')
            return HttpResponseRedirect(reverse('inventory:equipment_detail', args=[equipment.pk]))
        else:
            print(f"Form errors: {form.errors}")  # Debug
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EquipmentForm(instance=equipment)
    
    context = {
        'form': form,
        'equipment': equipment,
        'title': 'Edit Equipment',
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/equipment_form.html' if is_mobile_device(request) else 'inventory/equipment_form.html'
    return render(request, template, context)

# Quick status update API for mobile devices
@login_required
def quick_status_update(request, pk):
    """Update equipment status quickly from mobile."""
    if request.method == 'POST':
        equipment = get_object_or_404(Equipment, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status and new_status in dict(Equipment.STATUS_CHOICES):
            equipment.status = new_status
            equipment.save()
            messages.success(request, f'Status updated to {dict(Equipment.STATUS_CHOICES)[new_status]}')
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Enhanced mobile camera integration for scanning
@login_required
def scan_equipment(request):
    """Mobile-optimized scanning interface."""
    context = {
        'is_mobile': is_mobile_device(request),
    }
    return render(request, 'inventory/mobile/scan_interface.html', context)

@login_required
def equipment_delete(request, pk):
    """Delete an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        equipment_name = equipment.name
        equipment.delete()
        messages.success(request, f'Equipment "{equipment_name}" has been deleted.')
        return redirect('inventory:equipment_list')
    
    context = {
        'equipment': equipment,
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/equipment_confirm_delete.html' if is_mobile_device(request) else 'inventory/equipment_confirm_delete.html'
    return render(request, template, context)

@login_required
def equipment_qr(request, pk):
    """Generate QR code for equipment."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # Generate QR code for equipment URL
    equipment_url = request.build_absolute_uri(
        reverse('inventory:equipment_detail', kwargs={'pk': equipment.pk})
    )
    
    img = qrcode.make(equipment_url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'equipment': equipment,
        'qr_code_base64': qr_code_base64,
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/equipment_qr.html' if is_mobile_device(request) else 'inventory/equipment_qr.html'
    return render(request, template, context)

@login_required
def equipment_scan(request):
    """Scan equipment QR codes."""
    context = {
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/scan_interface.html' if is_mobile_device(request) else 'inventory/equipment_scan.html'
    return render(request, template, context)

@login_required
def equipment_scan_result(request):
    """Process equipment scan results."""
    equipment_id = request.GET.get('id')
    
    if equipment_id:
        try:
            equipment = Equipment.objects.get(pk=equipment_id)
            return redirect('inventory:equipment_detail', pk=equipment.pk)
        except Equipment.DoesNotExist:
            messages.error(request, "Equipment not found.")
    
    messages.error(request, "Invalid QR code scanned.")
    return redirect('inventory:equipment_list')

@login_required
def add_maintenance_record(request, pk):
    """Add a maintenance record to an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance_record = form.save(commit=False)
            maintenance_record.equipment = equipment
            maintenance_record.created_by = request.user
            maintenance_record.save()
            
            messages.success(request, "Maintenance record added successfully.")
            return redirect('inventory:equipment_detail', pk=equipment.pk)
    else:
        form = MaintenanceRecordForm()
    
    context = {
        'form': form,
        'equipment': equipment,
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/add_maintenance.html' if is_mobile_device(request) else 'inventory/add_maintenance.html'
    return render(request, template, context)

@login_required
def add_attachment(request, pk):
    """Add an attachment to an equipment item."""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.equipment = equipment
            attachment.uploaded_by = request.user
            attachment.save()
            
            messages.success(request, "Attachment added successfully.")
            return redirect('inventory:equipment_detail', pk=equipment.pk)
    else:
        form = AttachmentForm()
    
    context = {
        'form': form,
        'equipment': equipment,
        'is_mobile': is_mobile_device(request),
    }
    
    template = 'inventory/mobile/add_attachment.html' if is_mobile_device(request) else 'inventory/add_attachment.html'
    return render(request, template, context)
