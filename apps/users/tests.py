from django.test import TestCase
from django.core import mail
from apps.users.models import User
from apps.loyalty.models import LoyaltyCard

class UserRegistrationTest(TestCase):
    def test_user_creation_sends_activation_email(self):
        response = self.client.post('/users/register/',
            {
            'email': 'test3@mail.ru',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'patronymic': 'Иванов',
            'role': 'individual',
            'phone': '+79990012965',
            'password1': '147852Adnice!',
            'password2': '147852Adnice!',
            'agree_pd': True,
            'agree_rules': True,
        })
        self.assertRedirects(response, '/users/login/')
        self.assertTrue(User.objects.filter(email='test3@mail.ru').exists())
        user = User.objects.get(email='test3@mail.ru')
        self.assertFalse(user.is_active)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Подтверждение регистрации', mail.outbox[0].subject)

    def test_loyalty_card_and_wallet_created_for_individual(self):
        user = User.objects.create(
            email='test2@mail.ru',
            password='pass!123',
            role='individual',
            phone='+79995294429'
        )
        user.is_active = True
        user.save()
        self.assertTrue(hasattr(user, 'loyalty_card'))
        self.assertTrue(hasattr(user, 'coin_wallet'))
        self.assertEqual(user.loyalty_card.discount_level, 3)
        self.assertEqual(user.coin_wallet.balance, 0)


# Create your tests here.
