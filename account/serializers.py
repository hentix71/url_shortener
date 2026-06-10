from rest_framework import serializers
from .models import User



class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        write_only=True, 
        required=True
    )

class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for user response data."""
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
        ]
        read_only_fields = fields 
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            }

class LoginUserSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(
        required=True, 
        style =  
            {'input_type': 'email'}
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        min_length=8,
        style = 
            {'input_type': 'password'}
    )

class RegisterUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True, 
        min_length=8
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "confirm_password"]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            }

    def validate(self, attrs):
        errors = {}

        if attrs.get("password") != attrs.pop("confirm_password"):
            errors["confirm_password"] = "Password and Confirm Password do not match."
        
        if errors:
            print("Errors found in validation:")
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user