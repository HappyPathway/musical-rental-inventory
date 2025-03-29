from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    
    # Registration
    path('register/', views.register_customer, name='register'),
    
    # Staff management
    path('staff/create/', views.create_staff, name='create_staff'),
    path('staff/list/', views.staff_list, name='staff_list'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    
    # Profile management
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Password reset (using Django's built-in views)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
         
    # Admin user management (admin only)
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/<int:user_id>/change-type/', views.change_user_type, name='change_user_type'),
    path('admin/users/<int:user_id>/complete-staff-profile/', views.complete_staff_profile, name='complete_staff_profile'),
]