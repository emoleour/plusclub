from django.db import models
from django.conf import settings

class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='promotions/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-created_at']

    def __str__(self):
        return self.title



# Create your models here.
