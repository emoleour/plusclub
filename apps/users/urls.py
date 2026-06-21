from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<str:token>/', views.activate, name='activate'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/managers/', views.manager_list, name='manager_list'),
    path('admin/managers/create', views.manager_create, name='manager_create'),
    path('admin/managers/<int:pk>/edit', views.manager_update, name='manager_update'),
    path('admin/managers/<int:pk>/delete', views.manager_delete, name='manager_delete'),
    path('admin/admins/', views.admin_list, name='admin_list'),
    path('admin/admins/create', views.admin_create, name='admin_create'),
    path('admin/admins/<int:pk>/edit', views.admin_update, name='admin_update'),
    path('admin/admins/<int:pk>/delete', views.admin_delete, name='admin_delete'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            html_email_template_name='users/password_reset_email.html',
            subject_template_name='users/password_reset_subject.txt'
            ),
        name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ),
    name='password_reset_complete'),
]