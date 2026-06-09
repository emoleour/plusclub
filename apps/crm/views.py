from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .forms import SelectManagerForm
from .models import ManagerInstallerRelation

User = get_user_model()

@login_required
def select_manager(request):
    # Проверка, что пользователь — монтажник
    if request.user.role != 'installer':
        return redirect('profile')

    # Если уже выбрал менеджера — не показываем форму
    if hasattr(request.user, 'manager_relation'):
        return redirect('profile')

    form = None  # инициализируем до условий

    if request.method == 'POST':
        form = SelectManagerForm(request.POST)
        if form.is_valid():
            manager = form.cleaned_data['manager']
            ManagerInstallerRelation.objects.create(
                manager=manager,
                installer=request.user,
                confirmed=False
            )
            return redirect('profile')
        # если форма не валидна, остаёмся на странице, form уже определена
    else:
        form = SelectManagerForm()

    # в случае GET-запроса или невалидной POST-формы
    return render(request, 'crm/select_manager.html', {'form': form})

def is_manager(user):
    return user.role in ['manager', 'superadmin']

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):

    relations = ManagerInstallerRelation.objects.filter(manager=request.user).select_related('installer')
    pending = relations.filter(confirmed=False)
    confirmed = relations.filter(confirmed=True)

    context = {
        'pending': pending,
        'confirmed': confirmed,

    }
    return render(request, 'crm/manager_dashboard.html', context)

@login_required
@user_passes_test(is_manager)
def manager_confirm(request, pk):
    relation = get_object_or_404(ManagerInstallerRelation, pk=pk)

    if relation.manager != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        relation.confirmed = True
        relation.save()
        messages.success(request, f'Монтажник {relation.installer} подтвержден.')
        return redirect('manager_dashboard')
    return redirect('manager_dashboard')

@login_required
@user_passes_test(is_manager)
def manager_reject(request, pk):

    relation = get_object_or_404(ManagerInstallerRelation, pk=pk)
    if relation.manager != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        installer = relation.installer
        relation.delete()
        messages.warning(request, f'Связь с монтажником {installer} удалена.')
        return redirect('manager_dashboard')
    return redirect('manager_dashboard')

@login_required
@user_passes_test(is_manager)
def installer_detail(request, pk):

    installer = get_object_or_404(User, pk=pk, role='installer')

    relation = ManagerInstallerRelation.objects.filter(manager=request.user, installer=installer).first()
    if not relation:
        raise PermissionDenied

    context = {
        'installer': installer,
        'relation': relation,
        'purchases': [],
    }
    return render(request, 'crm/installer_detail.html', context)


# Create your views here.
