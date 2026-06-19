from rest_framework import permissions
from django.conf import settings

class HasAPIAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-KEY')
        return api_key == settings.API_SECRET_KEY