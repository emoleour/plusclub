from django.urls import path
from . import views

urlpatterns = [
    path('rewards/', views.reward_list, name='reward_list'),
    path('rewards/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
    path('coin-history/', views.coin_history, name='coin_history'),
    path('barcode/', views.barcode_image, name='barcode_image'),
]