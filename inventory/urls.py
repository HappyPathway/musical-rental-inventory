from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.equipment_list, name='list'),
    path('add/', views.equipment_add, name='add'),
    path('<int:pk>/', views.equipment_detail, name='detail'),
    path('<int:pk>/edit/', views.equipment_edit, name='edit'),
    path('<int:pk>/delete/', views.equipment_delete, name='delete'),
    path('qr/<int:pk>/', views.equipment_qr, name='qr'),
    path('scan/', views.equipment_scan, name='scan'),
    path('scan-result/', views.equipment_scan_result, name='scan_result'),
    path('<int:pk>/add-maintenance/', views.add_maintenance_record, name='add_maintenance'),
    path('<int:pk>/add-attachment/', views.add_attachment, name='add_attachment'),
]