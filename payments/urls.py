from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('create/<int:rental_id>/', views.payment_create, name='create'),
    path('<int:pk>/', views.payment_detail, name='detail'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', views.payment_webhook, name='webhook'),
    # Payment method specific paths
    path('paypal/create/<int:rental_id>/', views.paypal_create, name='paypal_create'),
    path('stripe/create/<int:rental_id>/', views.stripe_create, name='stripe_create'),
    path('venmo/create/<int:rental_id>/', views.venmo_create, name='venmo_create'),
]