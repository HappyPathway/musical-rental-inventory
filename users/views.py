from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import (
    CustomerRegistrationForm, StaffCreationForm, 
    CustomAuthenticationForm, UserProfileUpdateForm, UserUpdateForm,
    AdminUserTypeUpdateForm
)
from .models import UserProfile, StaffProfile, CustomerProfile
from django.http import HttpResponseRedirect
from django.db import transaction

# Helper functions for permission checks
def is_staff_member(user):
    """Check if user is an employee or admin"""
    if not user.is_authenticated:
        return False
    return user.profile.is_staff_member

def is_admin(user):
    """Check if user is an admin"""
    if not user.is_authenticated:
        return False
    return user.profile.user_type == 'admin'

# Custom decorators for view access control
def staff_required(view_func):
    """Decorator for views that require staff access"""
    decorated_view = user_passes_test(is_staff_member, login_url='users:login')(view_func)
    return decorated_view

def admin_required(view_func):
    """Decorator for views that require admin access"""
    decorated_view = user_passes_test(is_admin, login_url='users:login')(view_func)
    return decorated_view

# Login view
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                
                # Redirect based on user type
                if user.profile.is_staff_member:
                    return redirect('users:staff_dashboard')
                else:
                    return redirect('users:customer_dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

# Registration view for customers
def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify the authentication backend when calling login
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Account created successfully! Welcome to RokNSound, {user.get_full_name()}!")
            return redirect('users:customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

# Staff creation view - only accessible by admins
@admin_required
def create_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Staff account for {user.get_full_name()} created successfully!")
            return redirect('users:staff_list')
    else:
        form = StaffCreationForm()
    
    return render(request, 'users/create_staff.html', {'form': form})

# Staff list view - only accessible by admins
@admin_required
def staff_list(request):
    staff_profiles = UserProfile.objects.filter(user_type__in=['employee', 'admin'])
    return render(request, 'users/staff_list.html', {'staff_profiles': staff_profiles})

# Dashboard views based on user type
@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.profile.is_staff_member:
        return redirect('users:staff_dashboard')
    else:
        return redirect('users:customer_dashboard')

@login_required
def customer_dashboard(request):
    # Only allow customers to access
    if not request.user.profile.is_customer:
        messages.warning(request, "You don't have permission to access the customer dashboard.")
        return redirect('users:staff_dashboard')
    
    # Get customer's rental history and other relevant data
    # This would be expanded with actual rental/order data
    context = {
        'user': request.user,
    }
    return render(request, 'users/customer_dashboard.html', context)

@staff_required
def staff_dashboard(request):
    """Dashboard for employees and admins"""
    context = {
        'user': request.user,
        'is_admin': request.user.profile.user_type == 'admin',
    }
    return render(request, 'users/staff_dashboard.html', context)

# Profile management views
@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('users:view_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/update_profile.html', context)

@login_required
def view_profile(request):
    return render(request, 'users/view_profile.html')

# User management views for administrators
@admin_required
def user_list(request):
    """View all users - admin only"""
    # Get all users with their profiles
    users = User.objects.all().select_related('profile')
    return render(request, 'users/admin/user_list.html', {'users': users})

@admin_required
@transaction.atomic
def change_user_type(request, user_id):
    """Change a user's type/role - admin only"""
    user_to_change = get_object_or_404(User, id=user_id)
    
    # Don't allow changing your own user type to prevent locking yourself out
    if user_to_change == request.user:
        messages.error(request, "You cannot change your own user type.")
        return redirect('users:user_list')
    
    old_user_type = user_to_change.profile.user_type
    
    if request.method == 'POST':
        form = AdminUserTypeUpdateForm(request.POST, instance=user_to_change.profile)
        if form.is_valid():
            # Save the form which updates the user_type
            profile = form.save()
            new_user_type = profile.user_type
            
            # Update Django's is_staff flag for admin users
            if new_user_type == 'admin':
                user_to_change.is_staff = True
                user_to_change.save()
            elif old_user_type == 'admin' and new_user_type != 'admin':
                user_to_change.is_staff = False
                user_to_change.save()
            
            # If changed to staff role and no staff profile exists, redirect to create one
            if new_user_type in ['employee', 'admin'] and not hasattr(profile, 'staff_info'):
                messages.info(request, f"User type changed to {profile.get_user_type_display()}. Please complete the staff profile information.")
                return redirect('users:complete_staff_profile', user_id=user_id)
            
            messages.success(request, f"User type for {user_to_change.username} changed to {profile.get_user_type_display()}.")
            return redirect('users:user_list')
    else:
        form = AdminUserTypeUpdateForm(instance=user_to_change.profile)
    
    context = {
        'form': form,
        'user_to_change': user_to_change
    }
    return render(request, 'users/admin/change_user_type.html', context)

@admin_required
@transaction.atomic
def complete_staff_profile(request, user_id):
    """Complete staff profile information after changing user to staff type"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    # Redirect if user is not a staff member
    if not profile.is_staff_member:
        messages.error(request, "This user is not a staff member.")
        return redirect('users:user_list')
    
    # Check if staff profile already exists
    staff_profile, created = StaffProfile.objects.get_or_create(
        user_profile=profile,
        defaults={
            'employee_id': f"EMP{user.id:04d}",  # Default employee ID
            'position': 'Staff Member',
            'department': 'General',
            'hire_date': timezone.now().date()
        }
    )
    
    if request.method == 'POST':
        # Create a custom form for the staff profile fields
        staff_data = {
            'employee_id': request.POST.get('employee_id'),
            'position': request.POST.get('position'),
            'department': request.POST.get('department'),
            'hire_date': request.POST.get('hire_date')
        }
        
        # Basic validation
        if not all(staff_data.values()):
            messages.error(request, "All fields are required.")
        else:
            # Update the staff profile
            for key, value in staff_data.items():
                setattr(staff_profile, key, value)
            staff_profile.save()
            
            messages.success(request, f"Staff profile for {user.username} completed successfully.")
            return redirect('users:user_list')
    
    context = {
        'user': user,
        'staff_profile': staff_profile
    }
    return render(request, 'users/admin/complete_staff_profile.html', context)
