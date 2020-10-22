from django.urls import path
from .views import (UserRegistrationAPI,
                    UserLoginAPI,
                    ResetPasswordAPI,
                    UpdateProfileAPI,
                    UserDataAPI,
                    GenerateTokenAPI,
                    ValidateToken)

urlpatterns = [
    path('register/', UserRegistrationAPI.as_view(), name='register'),
    path('login/', UserLoginAPI.as_view(), name='login'),
    path('resetPassword/', ResetPasswordAPI.as_view(), name='resetPassword'),
    path('updateProfile/', UpdateProfileAPI.as_view(), name='updateProfile'),
    path('userData/', UserDataAPI.as_view(), name='userData'),
    path('generateToken/', GenerateTokenAPI.as_view(), name='generateToken'),
    path('validateToken/', ValidateToken.as_view(), name='validateToken'),
    ]
