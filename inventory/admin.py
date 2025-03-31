from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Equipment, MaintenanceRecord, EquipmentAttachment, SearchLog
from simple_history.admin import SimpleHistoryAdmin

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

@admin.register(Equipment)
class EquipmentAdmin(SimpleHistoryAdmin):
    list_display = ('image_thumbnail', 'name', 'brand', 'category', 'status_tag', 'rental_price_daily', 'serial_number')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('name', 'description', 'brand', 'serial_number', 'model_number')
    readonly_fields = ('qr_code_preview', 'qr_uuid', 'created_at', 'updated_at')
    list_per_page = 20
    save_on_top = True
    
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
