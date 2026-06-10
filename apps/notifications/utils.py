#from django.core.mail import send_mail
#from django.conf import settings
from .models import Notification


def create_notification(user, title, message, link=''):
    """Создает уведомление в базе"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link
    )
