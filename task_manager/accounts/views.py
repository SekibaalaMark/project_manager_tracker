from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
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
                "organization": user.organization.name if user.organization else None
                }
            , status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

