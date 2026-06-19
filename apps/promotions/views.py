from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse


from apps.notifications.utils import create_notification
from .models import Promotion
from .forms import PromotionForm


def is_admin(user):
    return user.role in ['admin', 'superadmin']

@login_required
@user_passes_test(is_admin)
def admin_promotion_list(request):
    promotions = Promotion.objects.all()
    return render(request, 'promotions/admin_promotion_list.html', {'promotions': promotions})

@login_required
@user_passes_test(is_admin)
def admin_promotion_create(request):
    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.created_by = request.user
            promotion.save()
            create_notification(
                user=request.user,
                title='Новая акция создана',
                message=f'Акция "{promotion.title}" успешно создана.',
                link=reverse('admin_promotion_list')
            )
            messages.success(request, 'Акция создана')
            return redirect('admin_promotion_list')
    else:
        form = PromotionForm()
    return render(request, 'promotions/admin_promotion_form.html', {'form': form, 'action': 'create'})

@login_required
@user_passes_test(is_admin)
def admin_promotion_update(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Акция обновлена')
            return redirect('admin_promotion_list')
    else:
        form = PromotionForm(instance=promotion)
    return render(request, 'promotions/admin_promotion_form.html', {'form': form, 'action': 'update', 'promotion': promotion})

@login_required
@user_passes_test(is_admin)
def admin_promotion_delete(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    if request.method == 'POST':
        promotion.delete()
        messages.success(request, 'Акция удалена')
        return redirect('admin_promotion_list')
    return render(request, 'promotions/admin_promotion_confirm_delete.html', {'promotions': promotion})

@login_required
def user_promotion_list(request):
    """Список активных акций для пользователей"""
    from django.utils import timezone
    now = timezone.now()
    promotions = Promotion.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)
    return render(request, 'promotions/user_promotion_list.html', {'promotions': promotions})


# Create your views here.
