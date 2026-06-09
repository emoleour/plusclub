from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('individual', 'Физическое лицо'),
        ('installer', 'Монтажник'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
        ('superadmin', 'Суперадмин'),
    ]

    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    phone = PhoneNumberField(
        blank=False,
        unique=True,
        verbose_name='Номер телефона'
    )
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    role = models.CharField(max_length=50, blank=True, choices=ROLE_CHOICES, verbose_name='Роль')
    is_active = models.BooleanField(default=False, verbose_name="Активен") # для монтажников до подтверждения
    is_staff = models.BooleanField(default=False, verbose_name='Статус персонала')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    accepted_terms_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата согласия с условиями') # дата принятия условий
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"


# Create your models here.
