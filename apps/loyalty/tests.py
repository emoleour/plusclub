from django.test import TestCase


from apps.users.models import User
from apps.loyalty.models import LoyaltyCard

class DiscountUpdateTest(TestCase):
    def test_discount_level_changes_on_total_spent_update(self):
        user = User.objects.create_user(
            email='client@test.ru',
            password='pass',
            role='individual',
            phone='+79990996587'
        )
        card = user.loyalty_card
        self.assertEqual(card.discount_level, 3)
        card.total_spent = 20000
        card.save()
        card.refresh_from_db()
        self.assertEqual(card.discount_level, 5)

        card.total_spent = 50000
        card.save()
        card.refresh_from_db()
        self.assertEqual(card.discount_level, 7)

        card.total_spent = 100000
        card.save()
        card.refresh_from_db()
        self.assertEqual(card.discount_level, 10)
