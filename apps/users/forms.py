from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('individual', 'Физическое лицо',), ('installer', 'Монтажник',)],
        label='Я регистрируюсь как',
        widget=forms.Select(attrs={'class': 'form_select'})
    )

    agree_pd = forms.BooleanField(
        label='Согласен на обработку персональных данных',
        required=True,
        error_messages={'required': 'Необходимо согласие на обработку ПД.'}
    )
    agree_rules = forms.BooleanField(
        label='Принимаю условия программы лояльности',
        required=True,
        error_messages={'required': 'Необходимо принять условия программы.'}
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'patronymic',
            'phone',
            'role',
            'password1',
            'password2',
        ]
        labels = {
            'email': 'Электронная почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'patronymic': 'Отчество',
            'phone': 'Номер телефона',
            'role': 'Я регистрируюсь как',
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field_name, field in self.fields.items():
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'form-check-input'
                else:
                    field.widget.attr['class'] = 'form-control'
        def clean_mail(self):
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
            return email

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocoplete': 'current-password',
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )

class ManagerForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Оставьте поле пустым, если не хотите менять пароль.'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'phone', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get('password1')
        pwd2 = cleaned_data.get('password2')
        if pwd1 or pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        if not user.pk:
            user.role = 'manager'

        password = self.cleaned_data.get('password1')

        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class AdminForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Оставьте поле пустым, если не хотите менять пароль'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'phone', 'is_active']

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get('password1')
        pwd2 = cleaned_data.get('password2')
        if pwd1 or pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError('Пароли не совпадают.')
        return cleaned_data
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit)
        if not user.pk:
            user.role = 'admin'
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
