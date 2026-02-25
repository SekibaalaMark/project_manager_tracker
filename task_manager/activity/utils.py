from .models import *


def log_activity(user, action, metadata=None):
    ActivityLog.objects.create(
        organization=user.organization,
        user=user,
        action=action,
        metadata=metadata or {}
    )