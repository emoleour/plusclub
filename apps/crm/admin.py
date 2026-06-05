from django.contrib import admin
from .models import ManagerInstallerRelation

@admin.register(ManagerInstallerRelation)
class ManagerInstallerRelationAdmin(admin.ModelAdmin):
    list_display = ('installer', 'manager', 'confirmed', 'created_at',)
    list_filter = ('confirmed',)
    search_fields = ('installer__email', 'manager__email',)



# Register your models here.
