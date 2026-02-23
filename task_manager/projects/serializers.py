from rest_framework import serializers
from .models import Project


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

        return task