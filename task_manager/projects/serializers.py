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
    


