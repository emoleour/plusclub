from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV-файл',
        help_text='Формат: email, дата (YYYY-MM-DD HH:MM), сумма, внешний ID (опционально)'
    )
    encoding = forms.CharField(
        initial='utf-8',
        max_length=20,
        label='Кодировка'
    )
    delimiter = forms.CharField(
        initial=',',
        max_length=5,
        label='Разделитель'
    )
    skip_header = forms.BooleanField(
        required=False,
        initial=True,
        label='Пропустить первую строку(заголовки)'
    )
