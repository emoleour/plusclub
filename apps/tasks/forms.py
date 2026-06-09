from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'reward_coins', 'deadline', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-contol'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'reward_coins': forms.NumberInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }