from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class LoyaltyCard(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_card',
        verbose_name='Пользователь'
    )
    card_number = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Номер карты'
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Общая сумма покупок'
    )
    discount_level = models.PositiveSmallIntegerField(
        default=3,
        verbose_name='Текущий уровень скидки'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Дисконтная карта'
        verbose_name = 'Дисконтные карты'

    def __str__(self):
        return f'Карта {self.card_number} ({self.user.email})'

    def update_discount_level(self):

        thresholds = [
            (0, 3),
            (20000, 5),
            (50000, 7),
            (100000, 10),
        ]
        new_level = 3
        for threshold, level in thresholds:
            if self.total_spent >= threshold:
                new_level = level
        if new_level != self.discount_level:
            self.discount_level = new_level
            self.save(update_fields=['discount_level'])

class CoinWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coin_wallet',
        verbose_name='Пользователь'
    )
    balance = models.PositiveIntegerField(default=0, verbose_name='Баланс коинов')

    class Meta:
        verbose_name = 'Кошелек Плюс Коинов'
        verbose_name_plural = 'Кошельки Плюс Коинов'

    def __str__(self):
        return f'Кошелек {self.user.email} ({self.balance} коинов)'


class CoinTransaction(models.Model):
    OPERATION_CHOICES = [
        ('earn', 'Начисление'),
        ('spend', 'Списание'),
    ]
    wallet = models.ForeignKey(
        CoinWallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Кошелек'
    )
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Сумма')
    operation = models.CharField(max_length=5, choices=OPERATION_CHOICES, verbose_name='Тип операции')
    reason = models.TextField(verbose_name='Основание')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Инициатор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата операции')

    class Meta:
        verbose_name = 'Транзакция коинов'
        verbose_name_plural = 'Транзакции коинов'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.operation == 'earn':
                self.wallet.balance += self.amount
            elif self.operation == 'spend':
                if self.wallet.balance < self.amount:
                    raise ValueError('Недостаточно коинов на балансе')
                self.wallet.balance -= self.amount
            self.wallet.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_operation_display()} {self.amount} коинов ({self.wallet.user.email})'

class Reward(models.Model):
    REWARD_TYPE_CHOICES = [
        ('discount', 'Скидка'),
        ('product', 'Товар'),
        ('merch', 'Мерч'),
        ('other', 'Другое'),
    ]
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    cost_in_coins = models.PositiveIntegerField(verbose_name='Цена в коинах')
    reward_type = models.CharField(
        max_length=20,
        choices=REWARD_TYPE_CHOICES,
        verbose_name='Тип вознаграждения'
    )
    discount_percent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Процент скидки (если применимо)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    class Meta:
        verbose_name = 'Вознаграждение'
        verbose_name_plural = 'Вознаграждения'

    def __str__(self):
        return f'{self.name} ({self.cost_in_coins} коинов)'


class InstallerPoint(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installer_points',
        verbose_name='Монтажник'
    )
    balance = models.PositiveIntegerField(default=0, verbose_name='Баланс баллов')

    class Meta:
        verbose_name = 'Баллы монтажника'
        verbose_name_plural = 'Баллы монтажников'

    def __str__(self):
        return f'{self.user.email} - {self.balance} баллов'

