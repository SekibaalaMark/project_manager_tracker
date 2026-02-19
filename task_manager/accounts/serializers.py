from rest_framework import serializers
from django.contrib.auth import get_user_model
from organizations.models import Organization
from django.utils.text import slugify
from django.db import transaction
import random

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirmation = serializers.CharField(write_only=True, style={'input_type': 'password'})
    organization_name = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that the two password fields match.
        """
        if data.get('password') != data.get('password_confirmation'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        # Remove confirmation field so it doesn't get passed to create_user
        validated_data.pop('password_confirmation')
        
        org_name = validated_data.get("organization_name")
        
        if org_name:
            with transaction.atomic():
                slug_base = slugify(org_name)
                unique_slug = f"{slug_base}-{random.randint(1000, 9999)}"
                org = Organization.objects.create(name=org_name, slug=unique_slug)
                
                user = User.objects.create_user(
                    username=validated_data["username"],
                    email=validated_data["email"],
                    password=validated_data["password"],
                    organization=org,
                    role="OWNER"
                )
        else:
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"]
            )

        return user