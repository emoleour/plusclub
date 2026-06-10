from django.urls import path
from . import views

urlpatterns = [
    path('rewards/', views.reward_list, name='reward_list'),
    path('rewards/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
    path('coin-history/', views.coin_history, name='coin_history'),
    path('barcode/', views.barcode_image, name='barcode_image'),
    path('admin/coins/', views.admin_coin_list, name='admin_coin_list'),
    path('admin/coins/transfer/', views.admin_coin_transfer_form, name='admin_coin_transfer'),
    path('admin/coins/transfer/process/', views.admin_coin_transfer_process, name='admin_coin_transfer_process'),
    path('admin/coins/history/', views.admin_coin_history, name='admin_coin_history'),
]