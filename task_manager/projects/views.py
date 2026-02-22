from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import *
from .serializers import *


class ManagerCreateProjectView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = ProjectCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectCreateSerializer(project).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)