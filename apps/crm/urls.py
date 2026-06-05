from django.urls import path
from . import views

urlpatterns = [
    path('select-manager/', views.select_manager, name='select_manager'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager-confirm/<int:pk>/', views.manager_confirm, name='manager_confirm'),
    path('manager-reject/<int:pk>/', views.manager_reject, name='manager_reject'),
    path('installer/<int:pk>/', views.installer_detail, name='installer_detail'),

]