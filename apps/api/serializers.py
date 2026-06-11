from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings


from apps.purchases.models import Purchase
from apps.products.models import Product
from apps.users.models import User
from apps.loyalty.models import LoyaltyCard, CoinWallet, CoinTransaction, Reward
from apps.tasks.models import Task, TaskSubmission
from apps.promotions.models import Promotion
from apps.notifications.models import Notification

signer = TimestampSigner()

class PurchaseSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'user_email', 'purchase_date', 'total_amount', 'external_id', 'items_data']

    def create(self, validated_data):
        email = validated_data.pop('user_email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_email': 'Пользователь не найден'})
        purchase =Purchase.objects.create(user=user, **validated_data)

        if hasattr(user, 'loyalty_card'):
            card = user.loyalty_card
            card.total_spend += purchase.total_amount
            card.update_discount_level()
            card.save()
        return purchase


class CustomerInfoSerializer(serializers.ModelSerializer):
    discount = serializers.IntegerField(source='loyalty_card.discout_level', default=0)
    coins = serializers.IntegerField(source='coin_wallet.balance', default=0)
    card_number = serializers.CharField(source='loyalty_card.card_number', default='')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'discount', 'coins', 'card_number']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('individual', 'Физическое лицо'), ('installer', 'Монтажник'),])

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'phone', 'role', 'password']

    def create(self, validated_data):
        password =validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        token = signer.sign(user.email)

        activation_url = f'{settings.BASE_URL or 'http://localhost:8000'}/api/v1/auth/activate/{token}/'
        send_mail(
            subject='Подтверждение регистрации в Плюс Клубе',
            message=f'Для активации перейдите по ссылке: {activation_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField()
    card_number = serializers.SerializerMethodField()
    coins = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'patronymic', 'phone', 'role', 'discount', 'card_number', 'coins']

    def get_discount(self, obj):
        if hasattr(obj,'loyalty_card'):
            return obj.loyalty_card.discount_level
        return 0

    def get_card_number(self, obj):
        if hasattr(obj, 'loyalty_card'):
            return obj.loyalty_card.card_number
        return 0

    def get_coins(self, obj):
        if hasattr(obj, 'coin_wallet'):
            return obj.coin_wallet.balance
        return 0


class CoinWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinWallet
        fields = ['balance']

class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = ['id', 'amount', 'operation', 'reason', 'created_at']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'name', 'description', 'cost_in_coins', 'reward_type', 'discount_percent']

class TaskSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'reward_coins', 'deadline', 'is_completed']

    def get_is_completed(self, obj):
        user = self.context['request'].user
        return TaskSubmission.objects.filter(task=obj, user=user).exists()

class TaskSubmissionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = TaskSubmission
        fields = ['id', 'task', 'task_title', 'photo', 'comment', 'status', 'created_at']
        read_only_fields = ['status']

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'image', 'start_date', 'end_date']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'link', 'is_read', 'created_at']


class ActivateAccountSerializer(serializers.Serializer):
    token = serializers.CharField()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'   # явно указываем, что используется email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переименовываем поле в 'email' для удобства клиентов
        self.fields['email'] = self.fields.pop('username')