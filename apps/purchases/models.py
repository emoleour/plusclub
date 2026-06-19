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
        unique=True,
        blank=True,
        null=True,
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


class PurchaseReturn(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='returns',
        verbose_name='Исходная покупка'
    )
    return_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма возврата'
    )
    reason = models.TextField(blank=True, verbose_name='Причина возврата')
    returned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата возврата')

    class Meta:
        verbose_name = 'Возврат покупки'
        verbose_name_plural = 'Возвраты покупок'
        ordering = ['-returned_at']

    def __str__(self):
        return f'Возврат по покупке {self.purchase.external_id} на сумму {self.return_amount}'


