from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import LoyaltyCard, CoinWallet
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
