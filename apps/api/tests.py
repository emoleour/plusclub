from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from apps.users.models import User
from apps.purchases.models import Purchase

@override_settings(API_SECRET_KEY='test_key')
class PurchaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='buyer@test.ru', password='pass', role='individual', phone='+79990000004'
        )
        self.url = '/api/v1/purchases/'

    def test_create_purchase_with_valid_api_key(self):
        response = self.client.post(
            self.url,
            {
                'user_email': 'buyer@test.ru',
                'purchase_date': '2026-06-19 12:00',
                'total_amount': 1500.00,
                'external_id': 'api-test-1',
                'items_data': [{'name': 'Товар', 'qty': 1, 'price': 1500}]
            },
            HTTP_X_API_KEY='test_key',
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Purchase.objects.filter(external_id='api-test-1').exists())

    def test_create_purchase_without_key_returns_401(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, 403)

# Create your tests here.
