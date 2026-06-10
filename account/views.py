from django.db import transaction

from rest_framework import status
from rest_framework.permissions import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics

from django.contrib.auth import authenticate

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from my_project.utils.custom_response import api_response
from my_project.utils.custom_permissions import IsOwner
from .serializers import *
from .models import User


# Logout user view
class LogoutUserView(generics.GenericAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = LogoutUserSerializer 

	@swagger_auto_schema(tags=["User Management"])
	def post(self, request, *args, **kwargs):
		try:
			serializer = self.get_serializer(data=request.data)
			if serializer.is_valid():
				refresh_token = serializer.validated_data.get('refresh')
				token = RefreshToken(refresh_token)
				token.blacklist()

				return api_response(
					status_code=status.HTTP_200_OK,
					is_success=True,
					message="Logout successful.",
					result=None
				)
			else:
				return api_response(
					status_code=status.HTTP_400_BAD_REQUEST,
					is_success=False,
					message="Invalid refresh token.",
					result=[serializer.errors]
				)
		except Exception as e:
			return api_response(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				is_success=False,
				message="Error occurred during logout.",
				result=[str(e)]
			)

# Login user view
class LoginUserView(generics.CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = LoginUserSerializer 

	@swagger_auto_schema(tags=["User Management"])
	def post(self, request, *args, **kwargs):
		try:
			serializer = self.get_serializer(data=request.data)
			
			if serializer.is_valid():
				email = serializer.validated_data.get('email')
				password = serializer.validated_data.get('password')

				user = authenticate(request, email=email, password=password)

				if user is not None:
					user_data = UserResponseSerializer(user).data

					# Generate JWT tokens
					refresh = RefreshToken.for_user(user)
			
					user_data['Access Token'] = str(refresh.access_token)
					user_data['Referesh Token'] = str(refresh)

					return api_response(
						status_code=status.HTTP_200_OK,
						is_success=True,
						message="Login successful.",
						result= user_data
					)
				else:
					return api_response(
						status_code=status.HTTP_401_UNAUTHORIZED,
						is_success=False,
						result= "Login Failed",
						message="Invalid email or password.",
					)
			else:
				return api_response(
					status_code=status.HTTP_400_BAD_REQUEST,
					is_success=False,
					message= "Login Failed Serializer invalid",
					result=[serializer.errors],
				)

		except Exception as e:
			return api_response(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				is_success=False,
				message="Error occurred during login.",
				result=[str(e)]
			)

# Register user view
class RegisterUserView(generics.CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = RegisterUserSerializer

	@transaction.atomic
	def perform_create(self, serializer):
		serializer.save()

	
	@swagger_auto_schema(tags=["User Management"])
	def post(self, request, *args, **kwargs):
		try:
			serializer = self.get_serializer(data=request.data)
			if serializer.is_valid():
				self.perform_create(serializer)
				return api_response(
					status_code=status.HTTP_201_CREATED,
					is_success=True,
					message="User registered successfully.",
					result=serializer.data
				)
			return api_response(
				status_code=status.HTTP_400_BAD_REQUEST,
				is_success=False,
				message=serializer.errors,
				result=None
			)
		except Exception as e:
			return api_response(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				is_success=False,
				message="Error occurred during registration.",
				result=[str(e)]
			)	