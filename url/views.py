from django.db import transaction

from rest_framework import status
from rest_framework.permissions import *
from rest_framework.generics import GenericAPIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from my_project.utils.custom_response import api_response
from my_project.utils.custom_permissions import IsOwner

from .serializers import *
from .models import *
from .services import url_service, redis_service


class ShortenURLAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShortenURLSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=["URL Management"])    
    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                short_url_obj = serializer.save()
                redis_service.cache_short_url(short_url_obj.short_code, short_url_obj.original_url)
                return api_response(
                    status_code=status.HTTP_201_CREATED,
                    is_success=True,
                    message="Short URL created successfully.",
                    result={
                        "short_code": short_url_obj.short_code,
                        "original_url": short_url_obj.original_url
                    }
                )
            else:
                return api_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    is_success=False,
                    message="Invalid data.",
                    result=[serializer.errors]
                )
        except Exception as e:
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                is_success=False,
                message="Error occurred while creating short URL.",
                result=[str(e)]
            )