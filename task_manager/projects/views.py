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
    




from rest_framework.generics import ListAPIView
from django.db.models import Count, Q

class OwnerDashboardView(ListAPIView):

    serializer_class = OwnerDashboardProjectSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user

        return (
            Project.objects
            .filter(organization=user.organization)
            .select_related("created_by")
            .annotate(
                total_tasks=Count("tasks"),
                completed_tasks=Count(
                    "tasks",
                    filter=Q(tasks__status="COMPLETED")
                )
            )
            .order_by("-created_at")
        )
    


class OwnerDashboardMetricsView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        org = request.user.organization

        project_stats = Project.objects.filter(
            organization=org
        ).aggregate(
            total_projects=Count("id"),
            pending_projects=Count("id", filter=Q(status="PENDING")),
            in_progress_projects=Count("id", filter=Q(status="IN_PROGRESS")),
            completed_projects=Count("id", filter=Q(status="COMPLETED")),
        )

        total_tasks = Task.objects.filter(
            organization=org
        ).count()

        data = {
            **project_stats,
            "total_tasks": total_tasks,
        }

        serializer = OwnerDashboardMetricsSerializer(data)
        return Response(serializer.data)
    





from django.db.models import Count, Q, F, FloatField, ExpressionWrapper
from accounts.models import CustomUser


class ManagerPerformanceAnalyticsView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        org = request.user.organization

        managers = CustomUser.objects.filter(
            organization=org,
            role="MANAGER"
        )

        analytics = []

        for manager in managers:

            projects = Project.objects.filter(
                organization=org,
                created_by=manager
            )

            total_projects = projects.count()

            pending_projects = projects.filter(
                status="PENDING"
            ).count()

            in_progress_projects = projects.filter(
                status="IN_PROGRESS"
            ).count()

            completed_projects = projects.filter(
                status="COMPLETED"
            ).count()

            tasks = Task.objects.filter(
                organization=org,
                project__created_by=manager
            )

            total_tasks = tasks.count()
            completed_tasks = tasks.filter(
                status="COMPLETED"
            ).count()

            completion_rate = (
                (completed_tasks / total_tasks) * 100
                if total_tasks > 0 else 0
            )

            analytics.append({
                "manager_id": manager.id,
                "username": manager.username,
                "total_projects": total_projects,
                "pending_projects": pending_projects,
                "in_progress_projects": in_progress_projects,
                "completed_projects": completed_projects,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(completion_rate, 2)
            })

        serializer = ManagerPerformanceSerializer(analytics, many=True)
        return Response(serializer.data)




'''
class ManagerPerformanceAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        org = request.user.organization

        # One query to rule them all
        analytics = CustomUser.objects.filter(
            organization=org, 
            role="MANAGER"
        ).annotate(
            # Count projects created by this manager
            total_projects=Count("created_projects", distinct=True),
            
            pending_projects=Count(
                "created_projects", 
                filter=Q(created_projects__status="PENDING"),
                distinct=True
            ),
            
            completed_projects=Count(
                "created_projects", 
                filter=Q(created_projects__status="COMPLETED"),
                distinct=True
            ),

            # Count tasks in projects created by this manager
            total_tasks=Count("created_projects__tasks", distinct=True),
            
            completed_tasks=Count(
                "created_projects__tasks", 
                filter=Q(created_projects__tasks__status="COMPLETED"),
                distinct=True
            )
        )

        # We still use many=True because we have a list of manager objects
        serializer = ManagerPerformanceSerializer(analytics, many=True)
        return Response(serializer.data)
'''