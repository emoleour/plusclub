import io
import barcode
from barcode.writer import ImageWriter
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reward, CoinWallet, CoinTransaction

@login_required
def barcode_image(request):
    """Генерация PNG со штрихкодом карты"""
    if not hasattr(request.user, 'loyalty_card'):
        return HttpResponse(status=404)
    card_number = request.user.loyalty_card.card_number
    code128 = barcode.get('code128', card_number, writer=ImageWriter())
    buffer = io.BytesIO()
    code128.write(buffer, options={
        'module_width': 0.3,
        'module_height': 8.0,
        'font_size': 8,
        'text_distance': 4.0,
    })
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

@login_required
def reward_list(request):
    rewards = Reward.objects.filter(is_active=True)
    wallet = request.user.coin_wallet
    return render(request, 'loyalty/reward_list.html', {'rewards': rewards, 'wallet': wallet})

@login_required
def redeem_reward(request, reward_id):
    reward = get_list_or_404(Reward, id=reward_id, is_active=True)
    wallet = request.user.coin_wallet
    if request.method == 'POST':
        if wallet.balance < reward.coin_in_coins:
            messages.error(request, 'Недостаточно коинов для обмена.')
            return redirect('reward_list')

        CoinTransaction.objects.create(
            wallet=wallet,
            amount=reward.cost_in_coins,
            operation='spend',
            reason=f'Обмен на вознаграждение: {reward.name}'
        )
        messages.success(request, f'Вы обменяли коины на "{reward.name}".')
        return redirect('reward_list')
    return redirect('reward_list')

@login_required
def coin_history(request):
    transactions = request.user.coin_wallet.transactions.order_by('-created_at')
    return render(request, 'loyalty/coin_history.html', {'transactions': transactions})




# Create your views here.
