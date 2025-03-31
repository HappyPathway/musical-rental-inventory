from django.contrib.admin import AdminSite
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from rentals.models import Customer, Rental, Contract
from rentals.admin import CustomerAdmin, RentalAdmin, ContractAdmin
from inventory.models import Category, Equipment, MaintenanceRecord, EquipmentAttachment, SearchLog
from inventory.admin import CategoryAdmin, EquipmentAdmin, MaintenanceRecordAdmin, SearchLogAdmin
from payments.models import Payment, PayPalTransaction, StripeTransaction, VenmoTransaction
from payments.admin import PaymentAdmin, PayPalTransactionAdmin, StripeTransactionAdmin, VenmoTransactionAdmin

class ROKNSOUNDAdminSite(AdminSite):
    site_header = "ROKNSOUND Management Portal"
    site_title = "ROKNSOUND Admin"
    index_title = "Welcome to ROKNSOUND Management Portal"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)
        
        # Sort the models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            
        # Sort the apps alphabetically
        app_list.sort(key=lambda x: x['name'].lower())
        
        return app_list
    
    def index(self, request, extra_context=None):
        """
        Override the index view to include key statistics for the dashboard
        """
        # Initialize extra_context if None
        extra_context = extra_context or {}
        
        # Get today's date
        today = timezone.now().date()
        
        # Get rental statistics
        from rentals.models import Rental
        extra_context['active_rentals'] = Rental.objects.filter(status='active').count()
        extra_context['overdue_rentals'] = Rental.objects.filter(status='overdue').count()
        extra_context['pending_rentals'] = Rental.objects.filter(status='pending').count()
        extra_context['completed_rentals'] = Rental.objects.filter(status='completed').count()
        
        # Get inventory statistics
        from inventory.models import Equipment
        extra_context['available_equipment'] = Equipment.objects.filter(status='available').count()
        extra_context['maintenance_equipment'] = Equipment.objects.filter(status='maintenance').count()
        extra_context['damaged_equipment'] = Equipment.objects.filter(status='damaged').count()
        
        # Get recent rentals
        extra_context['recent_rentals'] = Rental.objects.all().order_by('-created_at')[:5]
        
        # Get rentals due today
        extra_context['due_today'] = Rental.objects.filter(end_date=today, status='active')
        
        # Get recent payments
        from payments.models import Payment
        extra_context['recent_payments'] = Payment.objects.all().order_by('-payment_date')[:5]
        
        return super().index(request, extra_context)

# Create the admin site instance
roknsound_admin_site = ROKNSOUNDAdminSite(name='roknsound_admin')

# Register rental models with the custom admin site
roknsound_admin_site.register(Customer, CustomerAdmin)
roknsound_admin_site.register(Rental, RentalAdmin)
roknsound_admin_site.register(Contract, ContractAdmin)

# Register inventory models with the custom admin site
roknsound_admin_site.register(Category, CategoryAdmin)
roknsound_admin_site.register(Equipment, EquipmentAdmin)
roknsound_admin_site.register(MaintenanceRecord, MaintenanceRecordAdmin)
roknsound_admin_site.register(SearchLog, SearchLogAdmin)

# Register payment models with the custom admin site
roknsound_admin_site.register(Payment, PaymentAdmin)
roknsound_admin_site.register(PayPalTransaction, PayPalTransactionAdmin)
roknsound_admin_site.register(StripeTransaction, StripeTransactionAdmin)
roknsound_admin_site.register(VenmoTransaction, VenmoTransactionAdmin)