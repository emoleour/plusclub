import threading
from django.core.mail import send_mail
from django.conf import settings


def send_email_async(subject, message, recipient_list, from_email=None, fail_silently=True):

    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=fail_silently,
            )
        except Exception as e:
            print(f'Ошибка отправки письма: {e}')

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()