from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Payment, PayPalTransaction, StripeTransaction, VenmoTransaction

class PayPalTransactionInline(admin.StackedInline):
    model = PayPalTransaction
    can_delete = False
    verbose_name_plural = 'PayPal Transaction Details'
    readonly_fields = ('payment_completed_at', 'raw_response_formatted')
    fields = ('paypal_order_id', 'paypal_payer_id', 'paypal_payer_email', 'payment_completed_at', 'raw_response_formatted')
    
    def raw_response_formatted(self, obj):
        if obj.raw_response:
            return format_html('<pre style="max-height: 200px; overflow-y: auto; background-color: #1E1E1E; padding: 10px; border-radius: 4px;">{}</pre>', obj.raw_response)
        return "-"
    raw_response_formatted.short_description = "Raw Response"
    
class StripeTransactionInline(admin.StackedInline):
    model = StripeTransaction
    can_delete = False
    verbose_name_plural = 'Stripe Transaction Details'
    readonly_fields = ('raw_response_formatted',)
    fields = ('stripe_charge_id', 'stripe_customer_id', 'card_brand', 'card_last4', 'raw_response_formatted')
    
    def raw_response_formatted(self, obj):
        if obj.raw_response:
            return format_html('<pre style="max-height: 200px; overflow-y: auto; background-color: #1E1E1E; padding: 10px; border-radius: 4px;">{}</pre>', obj.raw_response)
        return "-"
    raw_response_formatted.short_description = "Raw Response"
    
class VenmoTransactionInline(admin.StackedInline):
    model = VenmoTransaction
    can_delete = False
    verbose_name_plural = 'Venmo Transaction Details'

@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'rental_link', 'customer_name', 'amount_formatted', 'payment_type_badge', 'payment_method_badge', 'status_badge', 'payment_date')
    list_filter = ('payment_type', 'payment_method', 'status', 'payment_date')
    search_fields = ('rental__customer__first_name', 'rental__customer__last_name', 'transaction_id', 'notes')
    readonly_fields = ('payment_date', 'transaction_details')
    date_hierarchy = 'payment_date'
    list_per_page = 20
    save_on_top = True
    
    fieldsets = (
        ('Rental Information', {
            'fields': ('rental',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'payment_type', 'payment_method', 'status')
        }),
        ('Transaction Information', {
            'fields': ('transaction_id', 'transaction_details')
        }),
        ('Additional Information', {
            'fields': ('notes', 'payment_date')
        }),
    )
    
    def rental_link(self, obj):
        if obj.rental:
            return format_html('<a href="/admin/rentals/rental/{}/change/">Rental #{}</a>', obj.rental.id, obj.rental.id)
        return "-"
    rental_link.short_description = "Rental"
    
    def customer_name(self, obj):
        if obj.rental and obj.rental.customer:
            customer = obj.rental.customer
            return format_html('<a href="/admin/rentals/customer/{}/change/">{}</a>',
                             customer.id, customer)
        return "-"
    customer_name.short_description = "Customer"
    
    def amount_formatted(self, obj):
        return format_html('<span style="font-weight: bold;">${:.2f}</span>', obj.amount)
    amount_formatted.short_description = "Amount"
    
    def payment_type_badge(self, obj):
        badge_colors = {
            'deposit': '#FFCE54',
            'rental': '#48CFAD',
            'late_fee': '#C23B23',
            'damage': '#C23B23',
            'refund': '#5D9CEC',
        }
        color = badge_colors.get(obj.payment_type, '#3A3A3A')
        return format_html('<span style="background-color:{}; color:#121212; padding:3px 8px; border-radius:4px; font-weight:bold;">{}</span>', 
                         color, obj.get_payment_type_display())
    payment_type_badge.short_description = "Payment Type"
    
    def payment_method_badge(self, obj):
        badge_colors = {
            'credit_card': '#5D9CEC',
            'cash': '#48CFAD',
            'paypal': '#3A3A3A',
            'stripe': '#5D9CEC',
            'venmo': '#3A3A3A',
            'check': '#FFCE54',
            'bank_transfer': '#5D9CEC',
        }
        color = badge_colors.get(obj.payment_method, '#3A3A3A')
        return format_html('<span style="background-color:{}; color:#121212; padding:3px 8px; border-radius:4px; font-weight:bold;">{}</span>', 
                         color, obj.get_payment_method_display())
    payment_method_badge.short_description = "Method"
    
    def status_badge(self, obj):
        badge_colors = {
            'pending': '#FFCE54',
            'completed': '#48CFAD',
            'failed': '#C23B23',
            'refunded': '#5D9CEC',
            'cancelled': '#3A3A3A',
        }
        color = badge_colors.get(obj.status, '#3A3A3A')
        return format_html('<span style="background-color:{}; color:#121212; padding:3px 8px; border-radius:4px; font-weight:bold;">{}</span>', 
                         color, obj.get_status_display())
    status_badge.short_description = "Status"
    
    def transaction_details(self, obj):
        if not obj.id:
            return "Transaction details will be available after saving."
            
        try:
            if obj.payment_method == 'paypal':
                paypal_tx = obj.paypal_transaction
                if not paypal_tx:
                    return "No PayPal transaction details found."
                return format_html(
                    '<div class="fieldset">'
                    '<div class="form-row"><div class="field-box"><label>PayPal Order ID:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Payer ID:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Payer Email:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Completed At:</label> <span>{}</span></div></div>'
                    '</div>',
                    paypal_tx.paypal_order_id,
                    paypal_tx.paypal_payer_id,
                    paypal_tx.paypal_payer_email,
                    paypal_tx.payment_completed_at,
                )
            elif obj.payment_method == 'stripe':
                stripe_tx = obj.stripe_transaction
                if not stripe_tx:
                    return "No Stripe transaction details found."
                return format_html(
                    '<div class="fieldset">'
                    '<div class="form-row"><div class="field-box"><label>Stripe Charge ID:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Customer ID:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Card:</label> <span>{} •••• {}</span></div></div>'
                    '</div>',
                    stripe_tx.stripe_charge_id,
                    stripe_tx.stripe_customer_id,
                    stripe_tx.card_brand,
                    stripe_tx.card_last4,
                )
            elif obj.payment_method == 'venmo':
                venmo_tx = obj.venmo_transaction
                if not venmo_tx:
                    return "No Venmo transaction details found."
                return format_html(
                    '<div class="fieldset">'
                    '<div class="form-row"><div class="field-box"><label>Venmo Transaction ID:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Username:</label> <span>{}</span></div></div>'
                    '<div class="form-row"><div class="field-box"><label>Email:</label> <span>{}</span></div></div>'
                    '</div>',
                    venmo_tx.venmo_transaction_id,
                    venmo_tx.venmo_username,
                    venmo_tx.venmo_email,
                )
            else:
                return "No detailed transaction information available for this payment method."
        except:
            return "Transaction details not available."
    transaction_details.short_description = "Transaction Details"
    
    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        
        if obj.payment_method == 'paypal':
            return [PayPalTransactionInline]
        elif obj.payment_method == 'stripe':
            return [StripeTransactionInline]
        elif obj.payment_method == 'venmo':
            return [VenmoTransactionInline]
        else:
            return []

@admin.register(PayPalTransaction)
class PayPalTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment_link', 'paypal_order_id', 'paypal_payer_email', 'payment_completed_at')
    search_fields = ('payment__rental__customer__first_name', 'payment__rental__customer__last_name', 
                    'paypal_order_id', 'paypal_payer_id', 'paypal_payer_email')
    readonly_fields = ('payment', 'payment_completed_at', 'raw_response_formatted')
    
    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">Payment #{}</a>', obj.payment.id, obj.payment.id)
    payment_link.short_description = "Payment"
    
    def raw_response_formatted(self, obj):
        if obj.raw_response:
            return format_html('<pre style="max-height: 400px; overflow-y: auto; background-color: #1E1E1E; padding: 10px; border-radius: 4px;">{}</pre>', obj.raw_response)
        return "-"
    raw_response_formatted.short_description = "Raw Response"

@admin.register(StripeTransaction)
class StripeTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment_link', 'stripe_charge_id', 'card_display', 'stripe_customer_id')
    search_fields = ('payment__rental__customer__first_name', 'payment__rental__customer__last_name', 
                    'stripe_charge_id', 'stripe_customer_id')
    readonly_fields = ('payment', 'raw_response_formatted')
    
    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">Payment #{}</a>', obj.payment.id, obj.payment.id)
    payment_link.short_description = "Payment"
    
    def card_display(self, obj):
        if obj.card_brand and obj.card_last4:
            return format_html('{} •••• {}', obj.card_brand, obj.card_last4)
        return "-"
    card_display.short_description = "Card"
    
    def raw_response_formatted(self, obj):
        if obj.raw_response:
            return format_html('<pre style="max-height: 400px; overflow-y: auto; background-color: #1E1E1E; padding: 10px; border-radius: 4px;">{}</pre>', obj.raw_response)
        return "-"
    raw_response_formatted.short_description = "Raw Response"

@admin.register(VenmoTransaction)
class VenmoTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment_link', 'venmo_transaction_id', 'venmo_username', 'venmo_email')
    search_fields = ('payment__rental__customer__first_name', 'payment__rental__customer__last_name', 
                    'venmo_transaction_id', 'venmo_username', 'venmo_email')
    readonly_fields = ('payment',)
    
    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">Payment #{}</a>', obj.payment.id, obj.payment.id)
    payment_link.short_description = "Payment"
