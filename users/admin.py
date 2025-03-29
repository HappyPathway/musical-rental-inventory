from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, CustomerProfile, StaffProfile

# Define inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Details'

class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Details'

# Define a new User admin with the inline profiles
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('profile__user_type',)
    
    def get_user_type(self, obj):
        return obj.profile.get_user_type_display()
    
    get_user_type.short_description = 'Role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        
        inlines = [UserProfileInline]
        if obj.profile.user_type == 'customer':
            inlines.append(CustomerProfileInline)
        elif obj.profile.user_type in ['employee', 'admin']:
            inlines.append(StaffProfileInline)
            
        return [inline(self.model, self.admin_site) for inline in inlines]

# Register the new UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register profile models separately
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'discount_rate')
    search_fields = ('user_profile__user__username', 'user_profile__user__email')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'employee_id', 'position', 'department', 'hire_date')
    list_filter = ('department', 'position')
    search_fields = ('user_profile__user__username', 'user_profile__user__email', 'employee_id')
