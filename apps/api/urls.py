from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename='task')
urlpatterns = [
    path('purchases/', views.PurchaseCreateAPIView.as_view(), name='api_purchase_create'),
    path('products/', views.ProductListCreateAPIView.as_view(), name='api_product_list'),
    path('customer-info/', views.CustomerInfoAPIView.as_view(), name='api_customer_info'),
    path('purchases/list/', views.PurchaseListAPIView.as_view(), name='api_purchase_list'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('wallet/', views.CoinWalletView.as_view(), name='wallet'),
    path('transactions/', views.CoinTransactionListView.as_view(), name='transactions'),
    path('rewards/', views.RewardListView.as_view(), name='rewards'),
    path('rewards/<int:reward_id>/redeem/', views.RedeemRewardView.as_view()),
    path('auth/activate/', views.ActivateAccountView.as_view(), name='auth_activate'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

]