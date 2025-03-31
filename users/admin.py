from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, CustomerProfile, StaffProfile

# Define inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fieldsets = (
        (None, {
            'fields': ('user_type', 'phone_number', 'address', 'city', 'state', 'zip_code')
        }),
    )

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Details'
    fieldsets = (
        (None, {
            'fields': ('preferred_payment_method', 'discount_rate', 'notes')
        }),
    )

class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Details'
    fieldsets = (
        ('Employment Details', {
            'fields': ('employee_id', 'position', 'department', 'hire_date')
        }),
    )

# Define a new User admin with the inline profiles
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'full_name', 'user_type_badge', 'is_active_icon', 'last_login_formatted')
    list_filter = ('is_active', 'profile__user_type', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    list_per_page = 20
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name or obj.last_name else "-"
    full_name.short_description = "Name"
    
    def user_type_badge(self, obj):
        badge_colors = {
            'customer': '#FFCE54',
            'employee': '#5D9CEC',
            'admin': '#C23B23',
        }
        if hasattr(obj, 'profile'):
            color = badge_colors.get(obj.profile.user_type, '#3A3A3A')
            return format_html('<span style="background-color:{}; color:#121212; padding:3px 8px; border-radius:4px; font-weight:bold;">{}</span>', 
                             color, obj.profile.get_user_type_display())
        return "-"
    user_type_badge.short_description = "Role"
    
    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#48CFAD;"><i class="fas fa-check-circle"></i></span>')
        return format_html('<span style="color:#C23B23;"><i class="fas fa-times-circle"></i></span>')
    is_active_icon.short_description = "Active"
    
    def last_login_formatted(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%Y-%m-%d %H:%M")
        return "Never"
    last_login_formatted.short_description = "Last Login"
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        
        inlines = [UserProfileInline]
        if hasattr(obj, 'profile'):
            if obj.profile.user_type == 'customer':
                inlines.append(CustomerProfileInline)
            elif obj.profile.user_type in ['employee', 'admin']:
                inlines.append(StaffProfileInline)
            
        return [inline(self.model, self.admin_site) for inline in inlines]
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Activity', {'fields': ('last_login', 'date_joined')}),
    )

# Register the new UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register profile models separately
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'user_type_badge', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'phone_number')
    
    def user_link(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.user.id, obj.user)
    user_link.short_description = "User"
    
    def user_type_badge(self, obj):
        badge_colors = {
            'customer': '#FFCE54',
            'employee': '#5D9CEC',
            'admin': '#C23B23',
        }
        color = badge_colors.get(obj.user_type, '#3A3A3A')
        return format_html('<span style="background-color:{}; color:#121212; padding:3px 8px; border-radius:4px; font-weight:bold;">{}</span>', 
                         color, obj.get_user_type_display())
    user_type_badge.short_description = "Role"

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'discount_rate', 'preferred_payment_method')
    search_fields = ('user_profile__user__username', 'user_profile__user__email')
    list_filter = ('discount_rate',)
    
    def user_display(self, obj):
        user = obj.user_profile.user
        name = f"{user.first_name} {user.last_name}" if user.first_name or user.last_name else user.username
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', user.id, name)
    user_display.short_description = "Customer"

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'employee_id', 'position', 'department', 'hire_date')
    list_filter = ('department', 'position', 'hire_date')
    search_fields = ('user_profile__user__username', 'user_profile__user__email', 'employee_id')
    date_hierarchy = 'hire_date'
    
    def user_display(self, obj):
        user = obj.user_profile.user
        name = f"{user.first_name} {user.last_name}" if user.first_name or user.last_name else user.username
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', user.id, name)
    user_display.short_description = "Employee"
