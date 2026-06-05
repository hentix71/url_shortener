from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# For Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="URL Shortener API",
        default_version="v1.0.0",
        description="""
            URL Shortener API documentation
        """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # swagger URL
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),

    # Admin URL
    path('admin/', admin.site.urls),

    # Local App URLs
]
