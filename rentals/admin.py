from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Customer, Rental, RentalItem, Contract

class RentalItemInline(admin.TabularInline):
    model = RentalItem
    extra = 1
    readonly_fields = ('returned_date', 'rental_item_price')
    fields = ('equipment', 'quantity', 'price', 'condition_note_checkout', 'returned', 'returned_date', 'condition_note_return')
    autocomplete_fields = ['equipment']
    
    def rental_item_price(self, obj):
        if obj.quantity and obj.price:
            total = obj.quantity * obj.price
            return f"${total:.2f} (${obj.price:.2f} × {obj.quantity})"
        return "-"
    rental_item_price.short_description = "Total Price"

@admin.register(Customer)
class CustomerAdmin(SimpleHistoryAdmin):
    list_display = ('get_full_name', 'email', 'phone', 'city', 'state', 'active_rentals')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('state', 'city')
    readonly_fields = ('created_at', 'updated_at', 'rental_history')
    list_per_page = 20
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
        ('Rental History', {
            'fields': ('rental_history',),
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rental_history(self, obj):
        rentals = obj.rentals.all().order_by('-start_date')
        if not rentals:
            return "No rental history."
        
        html = '<div style="max-height: 300px; overflow-y: auto;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #3A3A3A;"><th>ID</th><th>Date</th><th>Status</th><th>Items</th><th>Total</th></tr>'
        
        for rental in rentals:
            status_colors = {
                'pending': '#3A3A3A',
                'active': '#48CFAD',
                'overdue': '#C23B23',
                'completed': '#5D9CEC',
                'cancelled': '#777777',
            }
            status_style = f"background-color: {status_colors.get(rental.status, '#3A3A3A')}; color: #121212; padding: 2px 5px; border-radius: 3px; font-weight: bold;"
            
            html += f'<tr style="border-bottom: 1px solid #3A3A3A;">'
            html += f'<td><a href="/admin/rentals/rental/{rental.id}/change/">{rental.id}</a></td>'
            html += f'<td>{rental.start_date} to {rental.end_date}</td>'
            html += f'<td><span style="{status_style}">{rental.get_status_display()}</span></td>'
            html += f'<td>{rental.items.count()}</td>'
            html += f'<td>${rental.total_price}</td>'
            html += '</tr>'
        
        html += '</table></div>'
        return format_html(html)
    rental_history.short_description = "Rental History"
    
    def active_rentals(self, obj):
        active_count = obj.rentals.filter(status__in=['active', 'overdue']).count()
        if active_count:
            return format_html('<span style="background-color: #48CFAD; color: #121212; padding: 3px 8px; border-radius: 10px; font-weight: bold;">{}</span>', active_count)
        return format_html('<span style="color: #3A3A3A;">0</span>')
    active_rentals.short_description = "Active"

@admin.register(Rental)
class RentalAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'customer_link', 'rental_period', 'status_tag', 'item_count', 'total_price', 'deposit_status')
    list_filter = ('status', 'start_date', 'end_date', 'duration_type', 'deposit_paid')
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at', 'contract_signed_date', 'rental_items_summary')
    autocomplete_fields = ['customer']
    date_hierarchy = 'start_date'
    list_per_page = 20
    save_on_top = True
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Rental Period', {
            'fields': ('start_date', 'end_date', 'duration_type')
        }),
        ('Items', {
            'fields': ('rental_items_summary',)
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
    
    def rental_items_summary(self, obj):
        items = obj.items.all()
        if not items:
            return "No items in this rental."
        
        html = '<div style="max-height: 300px; overflow-y: auto;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #3A3A3A;"><th>Equipment</th><th>Quantity</th><th>Price</th><th>Status</th></tr>'
        
        for item in items:
            status = "Returned" if item.returned else "Out"
            status_color = "#48CFAD" if item.returned else "#FFCE54"
            status_style = f"background-color: {status_color}; color: #121212; padding: 2px 5px; border-radius: 3px;"
            
            html += f'<tr style="border-bottom: 1px solid #3A3A3A;">'
            html += f'<td><a href="/admin/inventory/equipment/{item.equipment.id}/change/">{item.equipment.name}</a></td>'
            html += f'<td>{item.quantity}</td>'
            html += f'<td>${item.price * item.quantity}</td>'
            html += f'<td><span style="{status_style}">{status}</span></td>'
            html += '</tr>'
        
        html += '</table></div>'
        return format_html(html)
    rental_items_summary.short_description = "Rental Items"
    
    def customer_link(self, obj):
        return format_html('<a href="/admin/rentals/customer/{}/change/">{}</a>', 
                         obj.customer.id, obj.customer)
    customer_link.short_description = "Customer"
    
    def rental_period(self, obj):
        days = (obj.end_date - obj.start_date).days
        return format_html('{} to {} <br><small>({} days - {})</small>', 
                         obj.start_date, obj.end_date, days, obj.get_duration_type_display())
    rental_period.short_description = "Rental Period"
    
    def status_tag(self, obj):
        status_colors = {
            'pending': '#3A3A3A',
            'active': '#48CFAD',
            'overdue': '#C23B23',
            'completed': '#5D9CEC',
            'cancelled': '#777777',
        }
        return format_html(
            '<span style="background-color: {}; color: #121212; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            status_colors.get(obj.status, '#3A3A3A'),
            obj.get_status_display()
        )
    status_tag.short_description = "Status"
    
    def deposit_status(self, obj):
        if obj.deposit_paid:
            return format_html('<span style="color: #48CFAD;"><i class="fas fa-check-circle"></i> Paid</span>')
        return format_html('<span style="color: #C23B23;"><i class="fas fa-times-circle"></i> Unpaid</span>')
    deposit_status.short_description = "Deposit"
    
    def item_count(self, obj):
        count = obj.items.count()
        total_quantity = sum(item.quantity for item in obj.items.all())
        return format_html('{} items<br><small>({} units)</small>', count, total_quantity)
    item_count.short_description = "Items"

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('rental', 'customer_name', 'generated_on', 'download_link')
    search_fields = ('rental__customer__first_name', 'rental__customer__last_name')
    readonly_fields = ('generated_on', 'preview_content')
    
    def customer_name(self, obj):
        return obj.rental.customer
    customer_name.short_description = "Customer"
    
    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" class="button" target="_blank">Download</a>', obj.file.url)
        return "No file"
    download_link.short_description = "Contract"
    
    def preview_content(self, obj):
        return format_html('<div style="max-height: 400px; overflow-y: auto; background-color: #1E1E1E; padding: 15px; border-radius: 5px;">{}</div>', obj.content)
    preview_content.short_description = "Contract Content"
    
    fieldsets = (
        (None, {
            'fields': ('rental', 'generated_on')
        }),
        ('Contract', {
            'fields': ('file', 'preview_content')
        }),
    )
