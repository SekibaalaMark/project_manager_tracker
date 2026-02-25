from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import *
from .models import *
from .serializers import *


class OrganizationActivityView(ListAPIView):

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ActivityLog.objects.filter(
            organization=self.request.user.organization
        )