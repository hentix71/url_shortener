from django.db import transaction

from rest_framework import status
from rest_framework.permissions import *
from rest_framework.generics import *
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import redirect
from django.http import Http404
from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from my_project.utils.custom_response import api_response
from my_project.utils.custom_permissions import IsOwner
from my_project.utils.pagination import CustomCursorPagination

from .serializers import *
from .models import *
from .services import url_service, redis_service


class RedirectURLAPIView(RetrieveAPIView):
    # redirect to the original URL based on the short code
    permission_classes = [AllowAny]
    serializer_class = ListURLSerializer
    lookup_field = 'short_code'
    queryset = ShortURL.objects.all()

    @swagger_auto_schema(tags=["URL Management"])
    def get(self, request, short_code):
        try:
            # First, check if the short code exists in the cache
            cached_data = redis_service.get_cached_short_url(short_code)

            if cached_data and cached_data.get("original_url"):
                original_url = cached_data.get("original_url")
                redis_service.increment_click_count(short_code)
                print(original_url)
                return redirect(original_url)
            
            else:
                instance = self.get_object()
                if instance.is_expired:
                    return api_response(
                        status_code=status.HTTP_410_GONE,
                        is_success=False,
                        message="This URL has expired.",
                        result=[]
                    )
                # Calculating the expiry time and Cacheing the short URL for future requests
                print(instance.expires_at, timezone.now())
                remaining_time = max(
                    int((instance.expires_at - timezone.now()).total_seconds()),
                    1
                )

                redis_service.cache_short_url(
                    instance.short_code, 
                    instance.original_url, 
                    timeout=remaining_time
                )

                # increment click count in cache and database
                redis_service.increment_click_count(instance.short_code)
                print(instance.original_url)
                return redirect(instance.original_url)
        except Http404:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                is_success=False,
                message="Short URL not found.",
                result=[]
            )
        except Exception as e:
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                is_success=False,
                message="Error occurred while redirecting.",
                result=[str(e)]
            )

class RetrieveURLAPIView(RetrieveAPIView):
    # retrieve a specific short URL and its whole row value

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ListURLSerializer
    lookup_field = 'short_code'
    queryset = ShortURL.objects.all()

    @swagger_auto_schema(tags=["URL Management"])    
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            serializer = self.get_serializer(instance)
            
            return api_response(
                status_code = status.HTTP_200_OK,
                is_success = True,
                message = "Short URL retrieved successfully.",
                result = serializer.data
            )
        except Http404:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                is_success=False,
                message="Short URL not found.",
                result=[]
            )
        except Exception as e:
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                is_success=False,
                message="Error occurred while retrieving the URL.",
                result=[str(e)]
            )
class UpdateURLAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UpdateURLSerializer
    lookup_field = 'short_code'
    queryset = ShortURL.objects.all()

    @swagger_auto_schema(tags=["URL Management"])    
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=["URL Management"])    
    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                updated_url = serializer.save()
                full_updated_data = ListURLSerializer(updated_url).data

                if updated_url.expires_at:
                        remaining_time = max(
                            int((updated_url.expires_at - timezone.now()).total_seconds()),
                            1
                        )
                else:
                    remaining_time = 1800  # default 30 minutes

                redis_service.cache_short_url(
                    updated_url.short_code, 
                    updated_url.original_url,
                    timeout=remaining_time
                )

                return api_response(
                    status_code=status.HTTP_200_OK,
                    is_success=True,
                    message="Short URL updated successfully.",
                    result= full_updated_data
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
                message="Error occurred while updating short URL.",
                result=[str(e)]
            )
class ListUserURLsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ListURLSerializer
    queryset = ShortURL.objects.all()
    pagination_class = CustomCursorPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['created_at', 'expires_at']
    search_fields = ['original_url', 'short_code']

    @swagger_auto_schema(tags=["URL Management"])    
    def get(self, request):
        try:
            return super().get(request)
        except Exception as e:
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                is_success=False,
                message="Error occurred while retrieving user URLs.",
                result=[str(e)]
            )

class ShortenURLAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShortenURLSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=["URL Management"])    
    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                short_url_obj = serializer.save()

                if short_url_obj.expires_at:
                    remaining_time = max(
                        int((short_url_obj.expires_at - timezone.now()).total_seconds()),
                        1
                    )
                else:
                    remaining_time = 1800  # default 30 minutes

                redis_service.cache_short_url(
                    short_url_obj.short_code, 
                    short_url_obj.original_url,
                    timeout=remaining_time
                )
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