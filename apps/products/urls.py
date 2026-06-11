from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_product_list, name='admin_product_list'),
    path('admin/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/<int:pk>/edit/', views.admin_product_update, name='admin_product_update'),
    path('admin/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('catalog/', views.product_catalog, name='product_catalog'),
]