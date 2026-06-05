from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SelectManagerForm(forms.Form):
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='manager', is_active=True),
        label='Выберите вашего менеджера',
        empty_label='--выберите--',
        widget=forms.Select(attrs={'class': 'form-select'})
    )