from django.urls import path, include

from . import views

urlpatterns = [
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('profile_update/', views.ProfileUpdateView.as_view(), name='profile_update'),
]

# path('register/', views.RegisterUserView.as_view(), name='register'),
