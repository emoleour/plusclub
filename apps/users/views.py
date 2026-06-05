from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm
from .models import User

signer = TimestampSigner()

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
            send_mail(
                subject='Подтверждение регистрации в Плюс Клуб',
                message=f"Для активации перейдите по ссылке:' {activation_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
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
    return render(request, 'users/profile.html', context)


