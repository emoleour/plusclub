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

    email = models.EmailField(unique=True)
    phone = PhoneNumberField(
        blank=False,
        unique=True,
        verbose_name='Номер телефона'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False) # для монтажников до подтверждения
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    accepted_terms_at = models.DateTimeField(auto_now_add=True) # дата принятия условий
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"


# Create your models here.
