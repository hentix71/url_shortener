from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path(
        'register/', 
        RegisterUserView.as_view(), 
        name='register'
    ),
    path(
        'login/', 
        LoginUserView.as_view(), 
        name='login'
    ),
    path(
        'token/refresh/', 
        TokenRefreshView.as_view(), 
        name='token_refresh'
    ),
    path(
        'logout/', 
        LogoutUserView.as_view(), 
        name='logout'
    ),   
]
