from django.urls import path, include
from .views import *

urlpatterns = [
    path('shorten/', ShortenURLAPIView.as_view(), name='shorten-url'),
    path('list-urls/', ListUserURLsAPIView.as_view(), name='list-user-urls'),
    path('retrieve/<str:short_code>/', RetrieveURLAPIView.as_view(), name='retrieve-url'),
    path('update/<str:short_code>/', UpdateURLAPIView.as_view(), name='update-url'), 

    path('redirect/<str:short_code>/', RedirectURLAPIView.as_view(), name='redirect-short-url'),
]
