from rest_framework import generics, status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView



from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


from apps.purchases.models import Purchase
from apps.products.models import Product
from apps.users.models import User
from apps.loyalty.models import CoinWallet, CoinTransaction, Reward
from apps.tasks.models import Task, TaskSubmission
from apps.promotions.models import Promotion
from apps.notifications.models import Notification
from .serializers import ProductSerializer, PurchaseSerializer, CustomTokenObtainPairSerializer
from . import serializers

User = get_user_model()
signer = TimestampSigner()


class PurchaseCreateAPIView(generics.CreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.API_SECRET_KEY:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.API_SECRET_KEY:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)

class CustomerInfoAPIView(APIView):

    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.API_SECRET_KEY:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        email = request.query_params.get('email')
        card_number = request.query_params.get('card_number')
        if not email and not card_number:
            return Response({'error': 'Укажите email или номер карты'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        elif card_number:
            try:
                user = User.objects.get(loyaty_card__card_number=card_number)
            except User.DoesNotExist:
                return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

            serializer = CustomerInfoAPIView(user)
            return Response(serializer.data)

class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = PurchaseSerializer

    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.API_SECRET_KEY:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Purchase.objects.all()
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        email = self.request.query_params.get('email')

        if start:
            queryset = queryset.filter(purchase_date__gte=start)

        if end:
            queryset = queryset.filter(purchase_date__lte=end)

        if email:
            queryset = queryset.filter(user__email=email)
        return queryset


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.UserRegisterSerializer

class ProfileView(generics.RetrieveAPIView):
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        return self.request.user

class CoinWalletView(generics.RetrieveAPIView):
    serializer_class = serializers. CoinWalletSerializer

    def get_object(self):
        return self.request.user.coin_wallet

class CoinTransactionListView(generics.ListAPIView):
    serializer_class = serializers.CoinTransactionSerializer

    def get_queryset(self):
        return self.request.user.coin_wallet.transactions.order_by('-created_at')


class RewardListView(generics.ListAPIView):
    queryset = Reward.objects.filter(is_active=True)
    serializer_class = serializers.RewardSerializer

class RedeemRewardView(generics.GenericAPIView):
    serializer_class = serializers.RewardSerializer

    def post(self, request, reward_id):
        reward = get_object_or_404(Reward, id=reward_id, is_active=True)
        wallet = request.user.coin_wallet
        if wallet.balance < reward.cost_in_coins:
            return Response({'error': 'Недостаточно коинов'}, status=status.HTTP_400_BAD_REQUEST)
        CoinTransaction.objects.create(
            wallet=wallet,
            amount=reward.cost_in_coins,
            operation='spend',
            reason=f'Обмен на {reward.name}'
        )
        return Response({'success': True, 'balance': wallet.balance})


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(is_active=True, deadline__gt=timezone.now())

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        task = self.get_object()
        if TaskSubmission.objects.filter(task=task, user=request.user).exists():
            return Response({'error': 'Уже выполнено'}, status=status.HTTP_400_BAD_REQUEST)
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'Фото обязательно'}, status=status.HTTP_400_BAD_REQUEST)

        comment = request.data.get('comment', '')
        submission = TaskSubmission.objects.create(
            task=task,
            user=request.user,
            photo=photo,
            comment=comment
        )
        return Response(serializers.TaskSubmissionSerializer(submission).data, status=201)

class TaskSubmissionListView(generics.ListAPIView):
    serializer_class = serializers.TaskSubmissionSerializer

    def get_queryset(self):
        return TaskSubmission.objects.filter(user=self.request.user).order_by('-created_at')


class PromotionListView(generics.ListAPIView):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = serializers.PromotionSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = serializers.ProductSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = serializers. NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.order_by('-created_at')

class NotificationReadAllView(generics.GenericAPIView):
    def post(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({'success': True})

class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def _activate_user(self, token):
        """Общая логика активации пользователя по токену."""
        try:
            email = signer.unsign(token, max_age=86400)  # 24 часа
        except SignatureExpired:
            return Response({'error': 'Срок действия ссылки истёк'}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({'error': 'Неверная ссылка активации'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({'message': 'Аккаунт уже активирован'})

        user.is_active = True
        user.save()
        return Response({'message': 'Аккаунт успешно активирован'})

    def post(self, request):
        """Активация через POST (токен в теле запроса)."""
        serializer = serializers.ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        return self._activate_user(token)

    def get(self, request, token=None):
        """Активация по прямой ссылке (токен в URL)."""
        return self._activate_user(token)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Если аккаунт существует, на почту отправлена инструкция'})

        token = signer.sign(user.email)
        reset_url = f'{settings.BASE_URL or "http://localhost:8000"}/api/v1/auth/password-reset/confirm/?token={token}'
        send_mail(
            subject='Сброс пароля в Плюс Клубе',
            message=f'Для сброса пароля перейдите по ссылке: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({'message': 'Если аккаунт существует, на почту отправлена инструкция'})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            email = signer.unsign(token, max_age=86400)
        except SignatureExpired:
            return Response({'error': 'Срок действия ссылки истек'}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({'error': 'Неверная ссылка для сброса пароля'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Пароль успешно изменен'})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
