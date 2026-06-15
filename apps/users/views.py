from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
#from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm, ManagerForm, AdminForm
from .models import User
from apps.purchases.models import Purchase
from .email_utils import send_email_async


signer = TimestampSigner()

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'manager':
            return redirect('manager_dashboard')
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        if request.user.role == 'superadmin':
            return redirect('admin_dashboard')
        else:
            return redirect('profile')
    else:
        return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # неактивен до подтв почты
            user.save()

            token = signer.sign(user.email)
            activation_url = request.build_absolute_uri(
                reverse('activate', kwargs={'token': token})
            )
            print(f'activation url: {activation_url}')

            #отправка письма
            send_email_async(
                subject='Подтверждение регистрации в Плюс Клуб',
                message=f"Для активации перейдите по ссылке:' {activation_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            messages.success(request, 'Регистрация прошла! Проверьте почту для активации.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def activate(request, token):

    try:

        email = signer.unsign(token, max_age=3600)
    except SignatureExpired:
        messages.error(request, 'Ссылка устарела. Запросите новую.')
        return redirect('register')
    except BadSignature:
        messages.error(request, 'Неверная ссылка активации')
        return redirect('register')

    user = get_object_or_404(User, email=email)
    if user.is_active:
        messages.info(request, 'Аккаунт уже активирован.')
        return redirect('login')

    user.is_active = True
    user.save()
    login(request, user)

    if user.role == 'installer':
        return redirect('select_manager')
    else:
        return redirect('profile')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')

            if user.role == 'installer':
                if not hasattr(user, 'manager_relation'):
                    return redirect('select_manager')
            return redirect('profile')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    context = {'user': user}

    if user.role == 'installer':
        if not hasattr(user, 'manager_relation'):
            return redirect('select_manager')
        context['relation'] = user.manager_relation
        context['manager_confirmed'] = user.manager_relation.confirmed
        context['manager'] = user.manager_relation.manager


    elif user.role == 'manager':
        return redirect('manager_dashboard')

    elif user.role in ('admin', 'superadmin'):
        return redirect('admin_dashboard')

    elif user.role == 'individual':
        if not hasattr(user, 'loyalty_card') or not hasattr(user, 'coin_wallet'):
            # Если сущности лояльности отсутствуют, перенаправляем на страницу с просьбой обратиться в поддержку
            # или создаём их вручную (здесь просто показываем предупреждение)
            context['error'] = 'Ваша дисконтная карта или кошелёк не найдены. Обратитесь в поддержку.'
            return render(request, 'users/profile.html', context)

        card = user.loyalty_card
        wallet = user.coin_wallet

        # Пороги скидок
        thresholds = [20000, 50000, 100000]
        next_threshold = next((t for t in thresholds if t > card.total_spent), None)

        if next_threshold:
            idx = thresholds.index(next_threshold)
            prev_threshold = thresholds[idx - 1] if idx > 0 else 0
            progress_percent = ((card.total_spent - prev_threshold) / (next_threshold - prev_threshold)) * 100
        else:
            progress_percent = 100
        next_discount_map = {3: 5, 5: 7, 7: 10}
        next_discount = next_discount_map.get(card.discount_level)

        context.update({
            'card': card,
            'progress_percent': min(progress_percent, 100),
            'next_threshold': next_threshold,
            'next_discount': next_discount,
            'wallet': wallet,
        })
        purchases = Purchase.objects.filter(user=user).order_by('-purchase_date')[:10]
        context['purchases'] = purchases

    return render(request, 'users/profile.html', context)

def is_admin(user):
    return user.role in ['admin', 'superadmin']

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    user = User.objects.get(pk=request.user.pk)
    context = {
        'is_superadmin': user.role == 'superadmin',
    }
    return render(request, 'users/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manager_list(request):
    managers = User.objects.filter(role='manager').order_by('last_name', 'first_name',)

    return render(request, 'users/manager_list.html', {'managers': managers})

@login_required
@user_passes_test(is_admin)
def manager_create(request):
    if request.method == 'POST':
        form = ManagerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Менеджер создан.')
            return redirect('manager_list')
    else:
        form = ManagerForm()
    return render(request, 'users/manager_form.html', {'form': form, 'action': 'create'})

@login_required
@user_passes_test(is_admin)
def manager_update(request, pk):
    manager = get_object_or_404(User, pk=pk, role='manager')
    if request.method == 'POST':
        form = ManagerForm(request.POST, instance=manager)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные менеджера обновлены.')
            return redirect('manager_list')
    else:
        form = ManagerForm(instance=manager)
    return render(request, 'users/manager_form.html', {'form': form, 'action': 'update', 'manager': manager})

@login_required
@user_passes_test(is_admin)
def manager_delete(request, pk):
    manager = get_object_or_404(User, pk=pk, role='manager')
    if request.method == 'POST':
        manager.is_active = False # деактивируем, без удаления из базы
        manager.save()
        messages.success(request, f'Менеджер {manager} деактивирован.')
        return redirect('manager_list')
    return render(request, 'users/manager_confirm_delete.html', {'manager': manager})

def is_superadmin(user):
    return user.role == 'superadmin'

@login_required
@user_passes_test(is_superadmin)
def admin_list(request):
    admins = User.objects.filter(role='admin').order_by('last_name', 'first_name')
    return render(request, 'users/admin_list.html', {'admins': admins})

@login_required
@user_passes_test(is_superadmin)
def admin_create(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Администратор создан.')
            return redirect('admin_list')
    else:
        form = AdminForm()
    return render(request, 'users/admin_form.html', {'form': form, 'action': 'create'})


@login_required
@user_passes_test(is_superadmin)
def admin_update(request, pk):
    admin_user = get_object_or_404(User, pk=pk, role='admin')
    if request.method == 'POST':
        form = AdminForm(request.POST, instance=admin_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные администратора обновлены.')
            return redirect('admin_list')
    else:
        form = AdminForm(instance=admin_user)
    return render(request, 'users/admin_form.html', {'form': form, 'action': 'update', 'admin': admin_user})

@login_required
@user_passes_test(is_superadmin)
def admin_delete(request, pk):
    admin_user = get_object_or_404(User, pk=pk, role='admin')
    if request.method == 'POST':
        admin_user.is_active = False
        admin_user.save()
        messages.success(request, f'Администратор {admin_user} деактивирован.')
        return redirect('admin_list')
    return render(request, 'users/admin_confirm_delete.html', {'admin_user': admin_user})
