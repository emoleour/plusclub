from django.db import models
from django.conf import settings
from django.utils import timezone

class Task(models.Model):

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    reward_coins = models.PositiveIntegerField(verbose_name='Награда (коины)')
    deadline = models.DateTimeField(verbose_name='Срок выполенения')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        return self.title

class TaskSubmission(models.Model):

    STATUS_CHOICES = [
        ('pending', 'На проверке'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions', verbose_name='Задание')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Пользователь'
    )
    photo = models.ImageField(upload_to='submissions/%Y/%m', verbose_name='Фотоотчет')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_submissions',
        verbose_name='Проверил'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата проверки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата выполнения')

    class Meta:
        verbose_name = 'Выполнение задания'
        verbose_name_plural = 'Выполнения заданий'

        unique_together = ['task', 'user']

    def __str__(self):
        return f'{self.user.email} - {self.task.title}'

    def approve(self, reviewer):
        """Одобрить задание: меняет статус и начисляет коины"""
        if self.status != 'pending':
            raise ValueError('Можно одобрить только ожидающее задание')
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()

        from apps.loyalty.models import CoinTransaction
        CoinTransaction.objects.create(
            wallet=self.user.coin_wallet,
            amount=self.task.reward_coins,
            operation='earn',
            reason=f'Выполнение задания: {self.task.title}'
        )
        from .models import MonthlyRating
        now = timezone.now()
        rating, created = MonthlyRating.objects.get_or_create(
            user=self.user,
            year=now.year,
            month=now.month
        )
        rating.completed_count = TaskSubmission.objects.filter(
            user=self.user,
            status='approved',
            created_at__year=now.year,
            created_at__month=now.year
        ).count()
        rating.save()

class MonthlyRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    completed_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'year', 'month']


# Create your models here.
