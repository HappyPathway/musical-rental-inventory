import csv
import io
from django import forms
from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Equipment, MaintenanceRecord, EquipmentAttachment, SearchLog
from simple_history.admin import SimpleHistoryAdmin
from django.urls import path
from django.template.response import TemplateResponse
from rentals.models import Rental
from inventory.models import Equipment

class EquipmentAttachmentInline(admin.TabularInline):
    model = EquipmentAttachment
    extra = 1
    verbose_name = "Attachment"
    verbose_name_plural = "Equipment Attachments"

class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 1
    verbose_name = "Maintenance Record"
    verbose_name_plural = "Maintenance History"

@admin.action(description='Export selected equipment to CSV')
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipment.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Brand', 'Category', 'Status', 'Rental Price (Daily)', 'Serial Number'])
    for equipment in queryset:
        writer.writerow([
            equipment.name,
            equipment.brand,
            equipment.category.name,
            equipment.get_status_display(),
            equipment.rental_price_daily,
            equipment.serial_number
        ])

    return response

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.action(description='Import equipment from CSV')
def import_from_csv(modeladmin, request, queryset):
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            next(reader)  # Skip header row

            for row in reader:
                try:
                    category, _ = Category.objects.get_or_create(name=row[2])
                    Equipment.objects.create(
                        name=row[0],
                        brand=row[1],
                        category=category,
                        status='available',
                        rental_price_daily=row[3],
                        serial_number=row[4]
                    )
                except Exception as e:
                    messages.error(request, f"Error importing row: {row}. Error: {e}")

            messages.success(request, "Equipment imported successfully.")
            return

    form = CSVImportForm()
    return render(request, 'admin/csv_form.html', {'form': form})

@admin.register(Equipment)
class EquipmentAdmin(SimpleHistoryAdmin):
    list_display = ('image_thumbnail', 'name', 'brand', 'category', 'status_tag', 'rental_price_daily', 'serial_number', 'has_manual')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('name', 'description', 'brand', 'serial_number', 'model_number')
    readonly_fields = ('qr_code_preview', 'qr_uuid', 'created_at', 'updated_at', 'manual_preview', 'manual_last_checked')
    list_per_page = 20
    save_on_top = True
    actions = [export_to_csv, 'fetch_manuals']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'brand', 'model_number', 'serial_number')
        }),
        ('Pricing', {
            'fields': ('rental_price_daily', 'rental_price_weekly', 'rental_price_monthly', 'deposit_amount')
        }),
        ('Status and Condition', {
            'fields': ('status', 'condition', 'notes')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'purchase_price')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('Manual', {
            'fields': ('manual_file', 'manual_title', 'manual_last_checked', 'manual_preview')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview', 'qr_uuid')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [EquipmentAttachmentInline, MaintenanceRecordInline]
    
    def image_thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.main_image.url)
        else:
            return format_html('<div style="width: 50px; height: 50px; background-color: #3A3A3A; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white;">No<br>Image</div>')
    image_thumbnail.short_description = ""
    
    def status_tag(self, obj):
        status_colors = {
            'available': '#48CFAD',
            'rented': '#FFCE54',
            'maintenance': '#5D9CEC',
            'damaged': '#C23B23',
            'retired': '#3A3A3A',
        }
        return format_html(
            '<span style="background-color: {}; color: #121212; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            status_colors.get(obj.status, '#3A3A3A'),
            obj.get_status_display()
        )
    status_tag.short_description = "Status"
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" /><br><a href="{}" target="_blank" class="button">Download QR Code</a>', obj.qr_code.url, obj.qr_code.url)
        return "QR code not generated yet."
    qr_code_preview.short_description = "QR Code Preview"
    
    def has_manual(self, obj):
        if obj.manual_file:
            return format_html('<span style="color: #48CFAD;"><i class="fas fa-check"></i></span>')
        return format_html('<span style="color: #C23B23;"><i class="fas fa-times"></i></span>')
    has_manual.short_description = "Manual"
    
    def manual_preview(self, obj):
        if obj.manual_file:
            last_checked = obj.manual_last_checked.strftime('%Y-%m-%d %H:%M') if obj.manual_last_checked else "Unknown"
            return format_html(
                '<div><a href="{}" target="_blank" class="button">Download Manual</a><br>'
                '<strong>Title:</strong> {}<br>'
                '<strong>Last Checked:</strong> {}</div>',
                obj.manual_file.url, obj.manual_title or 'No title', last_checked
            )
        return "No manual available."
    manual_preview.short_description = "Manual Preview"
    
    @admin.action(description='Fetch manuals for selected equipment')
    def fetch_manuals(self, request, queryset):
        from .utils import download_and_store_manual
        
        success_count = 0
        for equipment in queryset:
            if not equipment.manual_file and equipment.model_number:
                result = download_and_store_manual(equipment)
                if result:
                    success_count += 1
        
        if success_count:
            self.message_user(request, f"Successfully fetched {success_count} manuals.", level='SUCCESS')
        else:
            self.message_user(request, "Could not fetch any manuals. Verify the equipment has model numbers.", level='WARNING')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'equipment_count')
    search_fields = ('name', 'description')
    
    def equipment_count(self, obj):
        count = obj.equipment.count()
        return format_html('<a href="{}?category__id__exact={}">{} items</a>', 
                          '../equipment/', obj.id, count)
    equipment_count.short_description = "Equipment Count"

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('equipment_link', 'date', 'description', 'cost', 'performed_by')
    list_filter = ('date', 'equipment__category', 'equipment__brand')
    search_fields = ('description', 'performed_by', 'equipment__name')
    date_hierarchy = 'date'
    
    def equipment_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          f'../equipment/{obj.equipment.id}/change/', obj.equipment)
    equipment_link.short_description = "Equipment"

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ('query', 'app', 'user', 'created_at', 'results_count', 'ip_address')
    list_filter = ('app', 'created_at')
    search_fields = ('query', 'user__username', 'ip_address')
    readonly_fields = ('query', 'user', 'app', 'created_at', 'ip_address', 'results_count')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # Disable manual creation of search logs
        return False

# Register custom admin site name and branding
admin.site.site_header = "ROKNSOUND Management Portal"
admin.site.site_title = "ROKNSOUND Admin"
admin.site.index_title = "Welcome to ROKNSOUND Management Portal"

EquipmentAdmin.actions.append(import_from_csv)

# Override the admin index view
def custom_admin_index(request):
    context = {
        'active_rentals_count': Rental.objects.filter(status='active').count(),
        'overdue_rentals_count': Rental.objects.filter(status='overdue').count(),
        'pending_rentals_count': Rental.objects.filter(status='pending').count(),
        'completed_rentals_count': Rental.objects.filter(status='completed').count(),
        'available_inventory_count': Equipment.objects.filter(status='available').count(),
        'maintenance_inventory_count': Equipment.objects.filter(status='maintenance').count(),
        'damaged_inventory_count': Equipment.objects.filter(status='damaged').count(),
    }
    return TemplateResponse(request, 'admin/index.html', context)

# Update the admin site URLs
admin.site.get_urls = lambda: [
    path('', custom_admin_index, name='index'),
] + admin.site.get_urls()
