from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_promotion_list, name='admin_promotion_list'),
    path('admin/create/', views.admin_promotion_create, name='admin_promotion_create'),
    path('admin/<int:pk>/edit/', views.admin_promotion_update, name='admin_promotion_update'),
    path('admin/<int:pk>/delete/', views.admin_promotion_delete, name='admin_promotion_delete'),
    path('', views.user_promotion_list, name='user_promotion_list'),
]