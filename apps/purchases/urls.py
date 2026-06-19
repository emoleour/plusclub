from django.urls import path
from . import views

urlpatterns = [
    path('import-csv/', views.import_csv, name='import_csv'),
    path('<int:pk>/', views.purchase_detail, name='purchase_detail'),
]