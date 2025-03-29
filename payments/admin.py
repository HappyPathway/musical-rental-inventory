from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Payment, PayPalTransaction, StripeTransaction, VenmoTransaction

class PayPalTransactionInline(admin.StackedInline):
    model = PayPalTransaction
    can_delete = False
    verbose_name_plural = 'PayPal Transaction'
    
class StripeTransactionInline(admin.StackedInline):
    model = StripeTransaction
    can_delete = False
    verbose_name_plural = 'Stripe Transaction'
    
class VenmoTransactionInline(admin.StackedInline):
    model = VenmoTransaction
    can_delete = False
    verbose_name_plural = 'Venmo Transaction'

@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'rental', 'amount', 'payment_type', 'payment_method', 'status', 'payment_date')
    list_filter = ('payment_type', 'payment_method', 'status', 'payment_date')
    search_fields = ('rental__customer__first_name', 'rental__customer__last_name', 'transaction_id', 'notes')
    readonly_fields = ('payment_date',)
    
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
    list_display = ('payment', 'paypal_order_id', 'paypal_payer_email', 'payment_completed_at')
    search_fields = ('payment__rental__customer__first_name', 'payment__rental__customer__last_name', 
                    'paypal_order_id', 'paypal_payer_id', 'paypal_payer_email')
    readonly_fields = ('payment', 'payment_completed_at', 'raw_response')

@admin.register(StripeTransaction)
class StripeTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'stripe_charge_id', 'card_brand', 'card_last4')
    search_fields = ('payment__rental__customer__first_name', 'payment__rental__customer__last_name', 
                    'stripe_charge_id', 'stripe_customer_id')
    readonly_fields = ('payment', 'raw_response')

@admin.register(VenmoTransaction)
class VenmoTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'venmo_transaction_id', 'venmo_username', 'venmo_email')
    search_fields = ('payment__rental__customer__first_name', 'payment__rental__customer__last_name', 
                    'venmo_transaction_id', 'venmo_username', 'venmo_email')
    readonly_fields = ('payment',)
