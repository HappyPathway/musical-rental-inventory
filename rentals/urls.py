from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.rental_list, name='rental_list'),
    path('add/', views.rental_create, name='rental_create'),
    path('<int:pk>/', views.rental_detail, name='rental_detail'),
    path('<int:pk>/edit/', views.rental_edit, name='rental_update'),
    path('<int:pk>/return/', views.rental_return, name='rental_return'),
    path('<int:pk>/cancel/', views.rental_cancel, name='rental_cancel'),
    path('<int:pk>/contract/', views.rental_contract, name='rental_contract'),
    path('<int:pk>/sign/', views.rental_sign, name='rental_sign'),
]