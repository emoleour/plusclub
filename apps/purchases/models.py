from django.db import models
from django.conf import settings

class Purchase(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Покупатель'
    )
    purchase_date = models.DateTimeField(verbose_name='Дата покупки')
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма'
    )
    external_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Внешний ID (1C)'
    )
    items_data = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Список товаров'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'История покупок'
        ordering = ['-purchase_date']

    def __str__(self):
        return f'{self.user.email} - {self.total_amount} Р ({self.purchase_date:%d.%m.%Y})'


# Create your models here.
