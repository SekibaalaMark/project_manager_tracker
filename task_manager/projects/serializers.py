from rest_framework import serializers
from .models import Project
from activity.utils import *
from activity.utils import *
from notifications.utils import *


class ProjectCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ["id", "name", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        project = Project.objects.create(
            name=validated_data["name"],
            organization=user.organization,
            created_by=user,
            status="PENDING"
        )
        log_activity(
        user=user,
        action="Created Project",
        metadata={
        "project_id": project.id,
        "project_name": project.name
    }
)

        return project
    



from rest_framework import serializers
from .models import Task, Project
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["id", "title", "project", "assigned_to", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        project = data["project"]
        assigned_user = data["assigned_to"]

        # 1️⃣ Ensure project belongs to manager's organization
        if project.organization != user.organization:
            raise serializers.ValidationError(
                "Project does not belong to your organization."
            )

        # 2️⃣ Ensure manager created the project
        if project.created_by != user:
            raise serializers.ValidationError(
                "You can only create tasks under your own projects."
            )

        # 3️⃣ Ensure assigned user is in same organization
        if assigned_user.organization != user.organization:
            raise serializers.ValidationError(
                "Cannot assign task outside your organization."
            )

        # 4️⃣ Ensure assigned user is a MEMBER
        if assigned_user.role != "MEMBER":
            raise serializers.ValidationError(
                "Tasks can only be assigned to members."
            )

        return data

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        task = Task.objects.create(
            title=validated_data["title"],
            project=validated_data["project"],
            assigned_to=validated_data["assigned_to"],
            organization=user.organization,
            status="PENDING",
        )

        send_notification(
            validated_data["assigned_to"],
            f"You have been assigned a new task: {task.title}"
        )

        return task
    



class MemberTaskStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["status"]

    def validate_status(self, value):
        allowed_statuses = ["IN_PROGRESS", "COMPLETED"]


        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "You can only set status to IN_PROGRESS or COMPLETED."
            )

        return value

    def validate(self, data):
        

        request = self.context["request"]
        task = self.instance

        old_status = task.status
        new_status = data.get("status")


        

        # Ensure member only updates their own task
        if task.assigned_to != request.user:
            raise serializers.ValidationError(
                "You can only update tasks assigned to you."
            )
       
        log_activity(
                user=self.context["request"].user,
                action="Updated Task Status",
                metadata={
                    "task_id": task.id,
                    "old_status": old_status,
                    "new_status": new_status
                }
            )
        send_notification(
            task.project.created_by,
            f"Task '{task.title}' status changed to {task.status}"
                                                                    )

        return data



from django.db.models import Count, Q

class OwnerDashboardProjectSerializer(serializers.ModelSerializer):

    created_by = serializers.SerializerMethodField()
    total_tasks = serializers.IntegerField(read_only=True)
    completed_tasks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "status",
            "created_by",
            "total_tasks",
            "completed_tasks",
            "created_at",
        ]

    def get_created_by(self, obj):
        return {
            "id": obj.created_by.id,
            "username": obj.created_by.username,
            "email": obj.created_by.email,
        }
    

class OwnerDashboardMetricsSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    pending_projects = serializers.IntegerField()
    in_progress_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_tasks = serializers.IntegerField()



class ManagerPerformanceSerializer(serializers.Serializer):
    manager_id = serializers.IntegerField()
    username = serializers.CharField()
    total_projects = serializers.IntegerField()
    pending_projects = serializers.IntegerField()
    in_progress_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()