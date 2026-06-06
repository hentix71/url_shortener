from django.urls import path, include
from .views import *

urlpatterns = [
    path('shorten/', ShortenURLAPIView.as_view(), name='shorten-url'),
]
