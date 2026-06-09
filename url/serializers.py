from rest_framework import serializers
from .models import ShortURL
from .services.url_service import create_short_url
from django.utils import timezone

from django.core.cache import cache
class UpdateURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortURL
        fields = ['short_code', 'expires_at']

    def validate_short_code(self, value):
        if not value:
            return value
        
        value = value.lower().strip()
        if len(value) > 7:
            raise serializers.ValidationError("Short code must be no more than 7 characters long.")
        if not value.isalnum():
            raise serializers.ValidationError("Only letters and numbers allowed.")
        if ShortURL.objects.filter(short_code=value, is_active=True)\
            .exclude(id=self.instance.id)\
            .exists():
            raise serializers.ValidationError("Short code already exists.")
        return value

    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration time must be in the future.")
        return value

    def update(self, instance, validated_data):

        if instance.is_expired:
            raise serializers.ValidationError("Cannot update an expired URL.")

        if not validated_data or all(value is None for value in validated_data.values()):
            raise serializers.ValidationError("No data provided for update.")
        
        if all(getattr(instance, field) == value for field, value in validated_data.items()):
            raise serializers.ValidationError("Enter atleast one new value.")
                
        instance = super().update(instance, validated_data)
        return instance

class ListURLSerializer(serializers.ModelSerializer):
    click_count = serializers.IntegerField()
    class Meta:
        model = ShortURL
        fields = ['id', 'original_url', 'short_code', 'created_at', 'expires_at', 'click_count']

    def get_click_count(self, obj):
        
        pending_click_count = cache.get(
            f'clicks:{obj.short_code}',
            0
        )
        pending_click_count = int(pending_click_count or 0)
        return pending_click_count + obj.click_count

class ShortenURLSerializer(serializers.ModelSerializer):
    short_code = serializers.CharField(
        allow_blank=False,
        allow_null=True,
        required=False,
    )

    life_time = serializers.ChoiceField(
        required=False,
        choices=ShortURL.LifeDurationChoices.choices
    )

    class Meta:
        model = ShortURL
        fields = ['original_url', 'short_code', 'life_time']

    def validate_short_code(self, value):
        if not value:
            return value

        value = value.lower().strip()

        if len(value) > 7:
            raise serializers.ValidationError("Short code must be no more than 7 characters long.")
        if not value.isalnum():
            raise serializers.ValidationError("Only letters and numbers allowed.")
    
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        short_url_obj = create_short_url(user, validated_data)
        return short_url_obj
