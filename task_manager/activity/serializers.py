from rest_framework import serializers
from .models import *


class ActivityLogSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ["id", "action", "user", "metadata", "timestamp"]

    def get_user(self, obj):
        if obj.user:
            return {
                "id": obj.user.id,
                "username": obj.user.username,
                "role": obj.user.role
            }
        return None