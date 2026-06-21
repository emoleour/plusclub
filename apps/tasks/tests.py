from django.test import TestCase
from django.utils import timezone

from apps.users.models import User
from apps.tasks.models import Task, TaskSubmission
from apps.loyalty.models import CoinWallet

class TaskCompletionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.ru', password='pass', role='individual', phone='+79990000211'
        )
        self.admin = User.objects.create_user(
            email='admin@test.ru', password='pass', role='admin', phone='+79994521463'
        )
        self.task = Task.objects.create(
            title='Testovoe zadanie',
            description='opisanie',
            reward_coins=50,
            deadline=timezone.now() + timezone.timedelta(days=1),
            created_by=self.admin
        )
        self.submission = TaskSubmission.objects.create(
            task=self.task,
            user=self.user,
            photo='submissions/test.jpg',
            comment=''
        )
    def test_approve_submissions_adds_coins(self):
        wallet = self.user.coin_wallet
        initial_balance = wallet.balance
        self.submission.approve(self.admin)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, initial_balance + self.task.reward_coins)
        self.assertEqual(self.submission.status, 'approved')
