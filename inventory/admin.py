from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Category, Equipment, EquipmentAttachment, MaintenanceRecord

class EquipmentAttachmentInline(admin.TabularInline):
    model = EquipmentAttachment
    extra = 1

class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 1

@admin.register(Equipment)
class EquipmentAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'brand', 'category', 'status', 'rental_price_daily', 'serial_number')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('name', 'description', 'brand', 'serial_number', 'model_number')
    readonly_fields = ('qr_code', 'qr_uuid', 'created_at', 'updated_at')
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
            'fields': ('qr_code', 'qr_uuid')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [EquipmentAttachmentInline, MaintenanceRecordInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'date', 'description', 'cost', 'performed_by')
    list_filter = ('date', 'equipment')
    search_fields = ('description', 'performed_by', 'equipment__name')
