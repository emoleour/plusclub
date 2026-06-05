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
