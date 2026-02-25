from django.urls import path
from .views import *

urlpatterns = [
    path(
        "activity-logs/",OrganizationActivityView.as_view(),name="organization-activity"),
]