import io
import barcode
from barcode.writer import ImageWriter
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import Reward, CoinWallet, CoinTransaction
from apps.users.views import is_admin
from apps.notifications.utils import create_notification
from apps.loyalty.models import InstallerPoint

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

@login_required
@user_passes_test(is_admin)
def admin_coin_list(request):
    """Список пользователей с кошельками для ручного управления"""
    wallets = CoinWallet.objects.select_related('user').all().order_by('user__email')
    query = request.GET.get('q')
    if query:
        wallets = wallets.filter(user__email__icontains=query) | wallets.filter(user__first__name__icontains=query) | wallets.filter(
            user__last_name__icontains=query
        )
    return render(request, 'loyalty/admin_coin_list.html', {'wallets': wallets, 'query': query})

@login_required
@user_passes_test(is_admin)
def admin_coin_transfer_form(request):
    """ Страница для начисления/списания"""
    wallets = CoinWallet.objects.select_related('user').all().order_by('user__email')
    return render(request, 'loyalty/admin_coin_transfer.html', {'wallets': wallets})

@login_required
@user_passes_test(is_admin)
def admin_coin_transfer_process(request):
    """Обработка операции с коинами."""
    if request.method == 'POST':
        wallet_id = request.POST.get('wallet_id', '').strip()
        amount = request.POST.get('amount', '').strip()
        operation = request.POST.get('operation', '').strip()
        reason = request.POST.get('reason', '').strip()

        errors = []
        if not wallet_id:
            errors.append('Не выбран пользователь.')
        if not amount:
            errors.append('Не указана сумма.')
        else:
            try:
                amount_int = int(amount)
                if amount_int <= 0:
                    errors.append('Сумма должна быть положительной.')
            except ValueError:
                errors.append('Сумма должна быть целым числом.')
        if not operation:
            errors.append('Не выбран тип операции.')
        elif operation not in ['earn', 'spend']:
            errors.append('Неверный тип операции.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('admin_coin_transfer')

        try:
            wallet = CoinWallet.objects.select_related('user').get(id=int(wallet_id))
        except (CoinWallet.DoesNotExist, ValueError):
            messages.error(request, 'Кошелёк не найден.')
            return redirect('admin_coin_transfer')

        if operation == 'spend' and wallet.balance < amount_int:
            messages.error(request, 'Недостаточно коинов.')
            return redirect('admin_coin_transfer')

        CoinTransaction.objects.create(
            wallet=wallet,
            amount=amount_int,
            operation=operation,
            reason=reason,
            created_by=request.user
        )
        action = 'начислено' if operation == 'earn' else 'списано'
        create_notification(
            user=wallet.user,
            title='Изменение баланса коинов',
            message=f'Вам {action} {amount_int} коинов. Причина: {reason or "не указана"}.',
            link=reverse('profile')
        )
        messages.success(request, f'Пользователю {wallet.user.email} {action} {amount_int} коинов.')
        return redirect('admin_coin_list')

    return redirect('admin_coin_list')

@login_required
@user_passes_test(is_admin)
def admin_coin_history(request):
    """Историря всех транзакций для админа"""

    transactions = CoinTransaction.objects.select_related('wallet__user', 'created_by').order_by('-created_at')
    return render(request, 'loyalty/admin_coin_history.html', {'transactions': transactions})



@login_required
@user_passes_test(is_admin)
def admin_installer_points_list(request):
    points_list = InstallerPoint.objects.select_related('user').all().order_by('user__email')
    query = request.GET.get('q')
    if query:
        points_list = points_list.filter(
            Q(user__email__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    return render(request, 'loyalty/admin_installer_points_list.html', {'points_list': points_list, 'query': query})

@login_required
@user_passes_test(is_admin)
def admin_installer_points_transfer(request):
    if request.method == 'POST':
        points_id = request.POST.get('points_id')
        amount = request.POST.get('amount')
        operation = request.POST.get('operation')
        reason = request.POST.get('reason', '')

        if not points_id or not amount or not operation:
            messages.error(request, 'Заполните все поля')
            return redirect('admin_installer_points_list')

        try:
            points = InstallerPoint.objects.get(id=points_id)
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except (InstallerPoint.DoesNotExistm, ValueError):
            messages.error(request, 'Некорректные данные')
            return redirect('admin_installer_points_list')
        if operation == 'spend' and points.balance < amount:
            messages.error(request, 'Недостаточно баллов')
            return redirect('admin_installer_points_list')
        if operation == 'earn':
            points.balance += amount
        else:
            points.balance -= amount
        points.save()

        action = 'начислено' if operation == 'earn' else 'списано'
        messages.success(request, f'Монтажнику {points.user.email} {action} {amount} баллов. Причина {reason}.')
        return redirect('admin_installer_points_list')
    return redirect('admin_installer_points_list')


# Create your views here.
