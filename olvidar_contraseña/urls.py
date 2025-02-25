# olvidar_contraseña/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import PasswordResetRequestView, CustomPasswordResetConfirmView

urlpatterns = [
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='emails/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='emails/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
