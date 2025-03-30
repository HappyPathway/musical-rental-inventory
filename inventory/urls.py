from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('add/', views.equipment_add, name='equipment_add'),
    path('<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('qr/<int:pk>/', views.equipment_qr, name='equipment_qr'),
    path('scan/', views.equipment_scan, name='equipment_scan'),
    path('scan-result/', views.equipment_scan_result, name='equipment_scan_result'),
    path('<int:pk>/add-maintenance/', views.add_maintenance_record, name='add_maintenance'),
    path('<int:pk>/add-attachment/', views.add_attachment, name='add_attachment'),
]