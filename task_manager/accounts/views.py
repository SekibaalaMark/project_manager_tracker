from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data,context={"request": request})
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            user = data["user"]

            return Response({
                "message": "Login successful",
                "access": data["access"],
                "refresh": data["refresh"],
                "role": user.role,
                "must_change_password": user.must_change_password,
                "organization": user.organization.name if user.organization else None
                }
            , status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.permissions import IsAuthenticated
from .serializers import CreateOrganizationUserSerializer

class CreateOrganizationUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrganizationUserSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User created successfully",
                "username": user.username,
                "email": user.email,
                "role": user.role
            }, status=201)

        return Response(serializer.errors, status=400)




class SetNewPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetNewPasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password updated successfully"})
        
        return Response(serializer.errors, status=400)
    



from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .tokens import *


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=400)

        if email_verification_token.check_token(user, token):
            user.email_verified = True
            user.is_active = True
            user.save()

            return Response({"message": "Email verified successfully"})

        return Response({"error": "Invalid or expired token"}, status=400)