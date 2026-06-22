from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import LoyaltyCard, CoinWallet, InstallerPoint
import random
import string

def generate_card_number():
    return ''.join(random.choices(string.digits, k=16))

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_loyalty_entities(sender, instance, created, **kwargs):
    if created and instance.role == 'individual':
        LoyaltyCard.objects.create(
            user=instance,
            card_number=generate_card_number()
        )

        CoinWallet.objects.create(user=instance)

@receiver(post_save, sender=LoyaltyCard)
def auto_update_discount(sender, instance, created, **kwargs):
    """Автоматически пересчитывает скидку при изменении total_spent"""

    if not created:
        if hasattr(instance, '_old_total_spent'):
            if instance.total_spent != instance._old_total_spent:
                instance.update_discount_level()
        else:
            pass

@receiver(pre_save, sender=LoyaltyCard)
def store_old_total_spent(sender, instance, **kwargs):
    if instance.pk:
        old_instance = LoyaltyCard.objects.get(pk=instance.pk)
        instance._old_total_spent = old_instance.total_spent
    else:
        instance._old_total_spent = 0

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_installer_points(sender, instance, created, **kwargs):
    if created and instance.role == 'installer':
        InstallerPoint.objects.create(user=instance)
