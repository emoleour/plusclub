from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings


from apps.purchases.models import Purchase, PurchaseReturn
from apps.products.models import Product
from apps.users.models import User
from apps.loyalty.models import LoyaltyCard, CoinWallet, CoinTransaction, Reward
from apps.tasks.models import Task, TaskSubmission
from apps.promotions.models import Promotion
from apps.notifications.models import Notification
from apps.users.email_utils import send_email_async

signer = TimestampSigner()

class PurchaseSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)
    receipt = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Purchase
        fields = ['id', 'user_email', 'purchase_date', 'total_amount', 'external_id', 'items_data', 'receipt']

    def validate_items_data(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('items_data должен быть списком (массивом)')

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Каждый товар должен быть словарем')
            if 'name' not in item:
                raise serializers.ValidationError('У товара должно быть поле name')
        return value

    def create(self, validated_data):
        email = validated_data.pop('user_email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_email': 'Пользователь не найден'})
        purchase = Purchase.objects.create(user=user, **validated_data)

        if hasattr(user, 'loyalty_card'):
            card = user.loyalty_card
            card.total_spent += purchase.total_amount
            card.save()
        return purchase


class CustomerInfoSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField()
    coins = serializers.SerializerMethodField()
    card_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'discount', 'coins', 'card_number']

    def get_discount(self, obj):
        if hasattr(obj, 'loyalty_card'):
            return obj.loyalty_card.discount_level
        return 0
    def get_coins(self, obj):
        if hasattr(obj, 'coin_wallet'):
            return obj.coin_wallet.balance
        return 0
    def get_card_number(self, obj):
        if hasattr(obj, 'loyalty_card'):
            return obj.loyalty_card.card_number
        return ''


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

        activation_url = f'{settings.BASE_URL or "http://localhost:8000"}/api/v1/auth/activate/{token}/'
        send_email_async(
            subject='Подтверждение регистрации в Плюс Клубе',
            message=f'Для активации перейдите по ссылке: {activation_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
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

        self.fields['email'] = serializers.EmailField(label='Email')
        self.fields.pop('username', None)

class PurhcaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'purchase_date', 'total_amount', 'external_id', 'items_data']

class PurchaseReturnSerializer(serializers.ModelSerializer):
    external_id = serializers.CharField(write_only=True)

    class Meta:
        model = PurchaseReturn
        fields = ['external_id', 'return_amount', 'reason']

    def validate_external_id(self, value):
        try:
            purchase = Purchase.objects.get(external_id=value)
        except Purchase.DoesNotExist:
            raise serializers.ValidationError('Покупка с таким external_id не найдена')

        self.context['purchase'] = purchase
        return value

    def create(self, validated_data):
        purchase = self.context['purchase']
        validated_data.pop('external_id')
        return PurchaseReturn.objects.create(purchase=purchase, **validated_data)

class ApplyDiscountSerializer(serializers.Serializer):
    installer_id = serializers.IntegerField()
    type = serializers.IntegerField()
