from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from accounts import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.view_profile, name='profile'),

    path('reset-password/', PasswordResetView.as_view(
        template_name='accounts/reset_password.html'), {
        'email_template_name': 'accounts/reset_password_email.html',
        'success_url': reverse_lazy('accounts:password_reset_done')
    }, name='reset_password'),

    path('reset-password/done/', PasswordResetDoneView.as_view(
        template_name='accounts/reset_password_done.html'), name='password_reset_done'),

    path('reset-password/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetCompleteView.as_view(
        template_name='accounts/reset_password_complete.html'), name='password_reset_complete'),
    ]


