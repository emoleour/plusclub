from django.db import models
from django.conf import settings

class ManagerInstallerRelation(models.Model):
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installers',
        limit_choices_to={'role': 'manager', 'is_active': True}
    )

    installer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='manager_relation',
        limit_choices_to={'role': 'installer'}
    )

    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.installer} - {self.manager} ('подтверждён': {self.confirmed})"

# Create your models here.
