import csv
import io
import json
from datetime import datetime

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import CSVUploadForm
from .models import Purchase
from apps.users.models import User
#from apps.loyalty.models import LoyaltyCard


def is_admin(user):
    return user.role in ['admin', 'superadmin']

@login_required
@user_passes_test(is_admin)
def import_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            encoding = form.cleaned_data['encoding']
            delimiter = form.cleaned_data['delimiter']
            skip_header = form.cleaned_data['skip_header']

            try:
                data_set = csv_file.read().decode(encoding)
                io_string = io.StringIO(data_set)
                reader = csv.reader(io_string, delimiter=delimiter)

                created = 0
                updated_cards = set()
                if skip_header:
                    next(reader, None)


                for row in reader:
                    if not row or row[0].startswith('#'):
                        continue
                    try:
                        email = row[0].strip()
                        date_str = row[1].strip()
                        amount = float(row[2].strip())
                        external_id = row[3].strip() if len(row) > 3 else ''
                    except (IndexError, ValueError):
                        messages.warning(request, f'Пропущено некорректная строка: {row}')
                        continue

                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        messages.warning(request, f'Пользователь {email} не найден, строка пропущена.')

                        continue
                    try:
                        purchase_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                    except ValueError:
                        messages.warning(request, f'Неверный формат даты в строке {row}, пропущена.')

                        continue

                    ext_id = row[3].strip() if len(row) > 3 else ''
                    if ext_id and Purchase.objects.filter(external_id=ext_id).exists():
                        continue

                    items_json = row[4].strip() if len(row) > 4 else '[]'

                    try:
                        items = json.loads(items_json)
                    except json.JSONDecodeError:
                        items = []

                    Purchase.objects.create(
                        user=user,
                        purchase_date=purchase_date,
                        total_amount=amount,
                        external_id=external_id,
                        items_data=items,
                    )
                    created += 1

                    if hasattr(user, 'loyalty_card'):
                        card = user.loyalty_card
                        card.total_spent += amount
                        card.update_discount_level()
                        card.save()
                        updated_cards.add(card)
                messages.success(
                    request, f'Импортировано {created} покупок. Обновлено карт: {len(updated_cards)}.'
                )
            except Exception as e:
                messages.error(request, f'Ошибка при обработке файла: {e}')
    else:
        form = CSVUploadForm()
    return render(request, 'purchases/import_csv.html', {'form': form})


# Create your views here.
