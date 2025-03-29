from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.rental_list, name='list'),
    path('add/', views.rental_create, name='create'),
    path('<int:pk>/', views.rental_detail, name='detail'),
    path('<int:pk>/edit/', views.rental_edit, name='edit'),
    path('<int:pk>/return/', views.rental_return, name='return'),
    path('<int:pk>/contract/', views.rental_contract, name='contract'),
    path('<int:pk>/sign/', views.rental_sign, name='sign'),
]