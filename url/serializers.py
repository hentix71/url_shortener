from rest_framework import serializers
from .models import ShortURL
from .services.url_service import create_short_url

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
