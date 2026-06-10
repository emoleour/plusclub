import qrcode
import qrcode.image.svg
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
#from django.shortcuts import get_object_or_404

@login_required
def installer_qr_code(request, qr_type):
    """
    Генерирует QR-код для монтажников в зависимости от типа:
    1: скидка 10%
    2: скидка 5% + кешбэк 5%
    3: кешбэк 10%
    """
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

    import json
    qr_string = json.dumps(qr_data, ensure_ascii=False)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')
