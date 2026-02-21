from rest_framework import serializers
from django.contrib.auth import get_user_model
from organizations.models import Organization
from django.utils.text import slugify
from django.db import transaction
import random
from .utils import * 

User = get_user_model()
from .utils import send_temporary_password_email


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
                    role="OWNER",
                    is_active=False,   # IMPORTANT
                )
                
        else:
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"]
            )
        send_verification_email(self.context["request"], user)
        return user
    




from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        if user.role =="OWNER" and not user.email_verified:
            raise serializers.ValidationError("Please verify your email first.")

        # Generate JWT tokens manually
        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }





import random
import string
class CreateOrganizationUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    role = serializers.ChoiceField(choices=["MANAGER", "MEMBER"])

    def validate(self, data):
        request = self.context["request"]

        if request.user.role != "OWNER":
            raise serializers.ValidationError("Only OWNER can create users.")

        return data

    def create(self, validated_data):
        request = self.context["request"]

        # Generate temporary password
        temp_password = ''.join(random.choices(
            string.ascii_letters + string.digits, k=8
        ))

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=temp_password,
            organization=request.user.organization,
            role=validated_data["role"],
            must_change_password=True
        )

        send_temporary_password_email(user, temp_password)


        return user




class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if len(data["new_password"]) < 6:
            raise serializers.ValidationError("Password too short.")
        
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        
        return data

    def save(self, **kwargs):
        self.validated_data.pop("confirm_new_password")
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.must_change_password = False
        user.save()
        return user
    


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")

        self.user = user
        return data

    def save(self, **kwargs):
        send_verification_email(self.context["request"],self.user)
        return self.user