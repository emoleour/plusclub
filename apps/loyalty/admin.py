from django.contrib import admin
from .models import LoyaltyCard, CoinWallet, CoinTransaction, Reward

admin.site.register(LoyaltyCard)
admin.site.register(CoinWallet)
admin.site.register(CoinTransaction)
admin.site.register(Reward)

# Register your models here.
