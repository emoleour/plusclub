from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('<int:task_id>', views.task_detail, name='task_detail'),
    path('history/', views.submission_history, name='submission_history'),
    path('rating/', views.mothly_rating, name='monthly_rating'),
    path('admin/review/', views.review_list, name='review_list'),
    path('admin/review/<int:submission_id>/', views.review_detail, name='review_detail'),
    path('admin/manage/', views.task_manage_list, name='task_manage_list'),
    path('admin/manage/create/', views.task_manage_create, name='task_manage_create'),
    path('admin/manage/<int:task_id>/edit/', views.task_manage_update, name='task_manage_update'),
    path('admin/manage/<int:task_id>/delete/', views.task_manage_delete, name='task_manage_delete'),
]
