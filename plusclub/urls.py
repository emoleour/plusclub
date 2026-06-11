"""
URL configuration for plusclub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.users.views import home_redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from apps.api.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('users/', include('apps.users.urls')),
    path('crm/', include('apps.crm.urls')),
    path('loyalty/', include('apps.loyalty.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('purchases/', include('apps.purchases.urls')),
    path('promotions/', include('apps.promotions.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('products/', include('apps.products.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include('apps.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]


