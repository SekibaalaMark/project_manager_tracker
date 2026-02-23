from django.urls import path
from .views import *

urlpatterns = [
    path("create-project/",ManagerCreateProjectView.as_view(),name="manager-create-project",),
    path("create-tasks/",ManagerCreateTaskView.as_view(),name="manager-create-task",),
    path("<int:id>/update-status/",MemberUpdateTaskStatusView.as_view(),
         name="member-update-task-status",),
    
]