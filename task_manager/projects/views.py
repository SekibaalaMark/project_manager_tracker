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
    




class ManagerCreateTaskView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = TaskCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            task = serializer.save()
            return Response(
                TaskCreateSerializer(task).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



from rest_framework.generics import UpdateAPIView

class MemberUpdateTaskStatusView(UpdateAPIView):

    serializer_class = MemberTaskStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsMember]
    lookup_field = "id"

    def get_queryset(self):
        # Member can only access their own tasks
        return Task.objects.filter(
            assigned_to=self.request.user,
            organization=self.request.user.organization
        )