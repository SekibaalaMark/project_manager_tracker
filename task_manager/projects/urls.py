from django.urls import path
from .views import ManagerCreateProjectView

urlpatterns = [
    path("create/",ManagerCreateProjectView.as_view(),name="manager-create-project",),
]