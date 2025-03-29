from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Customer, Rental, RentalItem, Contract

class RentalItemInline(admin.TabularInline):
    model = RentalItem
    extra = 1
    readonly_fields = ('returned_date',)

@admin.register(Customer)
class CustomerAdmin(SimpleHistoryAdmin):
    list_display = ('get_full_name', 'email', 'phone', 'city', 'state')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('state', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('ID Information', {
            'fields': ('id_type', 'id_number', 'id_image')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Rental)
class RentalAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'customer', 'start_date', 'end_date', 'status', 'total_price')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at', 'contract_signed_date')
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Rental Period', {
            'fields': ('start_date', 'end_date', 'duration_type')
        }),
        ('Financial Information', {
            'fields': ('total_price', 'deposit_total', 'deposit_paid')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Contract', {
            'fields': ('contract_signed', 'contract_signed_date', 'contract_signature_data')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [RentalItemInline]

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('rental', 'generated_on')
    search_fields = ('rental__customer__first_name', 'rental__customer__last_name')
    readonly_fields = ('generated_on',)
