from django.contrib import admin
from .models import LoyaltyCard, CoinWallet, CoinTransaction, Reward, InstallerPoint

admin.site.register(LoyaltyCard)
admin.site.register(CoinWallet)
admin.site.register(CoinTransaction)
admin.site.register(Reward)
admin.site.register(InstallerPoint)

# Register your models here.
