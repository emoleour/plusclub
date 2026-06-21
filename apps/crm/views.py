import json
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample


from .forms import SelectManagerForm
from .models import ManagerInstallerRelation
from apps.purchases.models import Purchase
from apps.notifications.utils import create_notification
from apps.api.permissions import HasAPIAccess
from apps.api.serializers import ApplyDiscountSerializer

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
        create_notification(
        user=relation.installer,
        title='Аккаунт подтвержден',
        message=f'Менеджер {relation.manager.get_full_name()} подтвердил вашу регистрацию',
        link=reverse('profile')
    )

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
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchase_date')[:10]

    context = {
        'installer': installer,
        'relation': relation,
        'purchases': purchases,
    }
    return render(request, 'crm/installer_detail.html', context)



class ApplyInstallerDiscountView(APIView):
    """"
    Возращает JSON с описанием скидки/кешбэка для кассы
    """
    permission_classes = [HasAPIAccess]
    authentication_classes = []
    @extend_schema(
            request=ApplyDiscountSerializer,
            examples=[
                OpenApiExample(
                    'Пример запроса',
                    value={'installer_id': 42, 'type': 1},
                    request_only=True
                )
            ],
            responses={200: dict},
            description='Применить скидку/кешбэк монтажника'
    )

    def post(self, request, format=None):
        installer_id = request.data.get('installer_id')
        qr_type = request.data.get('type')

        if not installer_id or not qr_type:
            return Response(
                {'error': 'installer_id и type обязательны'}
            )

        try:
            user = User.objects.get(id=installer_id, role='installer', is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Монтажник не найден или неактивен'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not hasattr(user, 'manager_relation') or not user.manager_relation.confirmed:
            return Response(
                {'error': 'Монтажник не подтвержден'},
                status=status.HTTP_403_FORBIDDEN
            )

        #формируем тип скидки
        if qr_type == 1:
            discount_percent = 10
            cashback_percent = 0
            description = 'Скидка 10%'
        elif qr_type == 2:
            discount_percent = 5
            cashback_percent = 5
            description = 'Скидка 5% + кешбэк 5%'
        elif qr_type == 3:
            discount_percent = 0
            cashback_percent = 10
            description = 'Кэшбек 10%'
        else:
            return Response(
                {'error': 'Неизвестный тип скидки'},
                status=status.HTTP_400_BAD_REQUEST
            )

        #формируем ответ для 1С
        return Response({
            'installer_id': user.id,
            'installer_email': user.email,
            'installer_name': f'{user.last_name} {user.first_name}',
            'discount_percent': discount_percent,
            'cashback_percent': cashback_percent,
            'description': description,
            'message': f'Применить {description} к текущей покупке'
        }, status=status.HTTP_200_OK)


@login_required
def installer_qr_code(request, qr_type):
    """Генерация qr-code монтажником"""
    user = request.user
    if user.role != 'installer':
        return HttpResponse(status=404)

    if not hasattr(user, 'manager_relation') or not user.manager_relation.confirmed:
        return HttpResponse(status=403)

    qr_data = {
        'installer_id': user.id,
        'type': qr_type,
        'description': '',
    }
    if qr_type == 1:
        qr_data['description'] = 'discount_10'
    elif qr_type == 2:
        qr_data['description'] = 'discount_5_cashback_5'
    elif qr_type == 3:
        qr_data['description'] = 'cashback_10'
    else:
        return HttpResponse(status=404)

    qr_string = json.dumps(qr_data, ensure_ascii=False)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#F5C518', back_color='#121212')

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')
