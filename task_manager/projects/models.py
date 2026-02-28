from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

from django_q.tasks import async_task
from notifications.utils import send_system_email



class Project(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    )

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="projects"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_projects"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self):
        tasks = self.tasks.all()

        if not tasks.exists():
            self.status = "PENDING"

        elif all(task.status == "COMPLETED" for task in tasks):
            self.status = "COMPLETED"
            async_task(
                    send_system_email,
                    "Project Completed",
                    f"Project '{self.name}' has been completed.",
                    [self.created_by.email],
                )

        elif any(task.status != "PENDING" for task in tasks):
            self.status = "IN_PROGRESS"

        else:
            self.status = "PENDING"

        self.save(update_fields=["status"])

    def __str__(self):
        return self.name
    


class Task(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    )

    title = models.CharField(max_length=255)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_tasks"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # 1. Logic Check: Auto-assign the Task's organization to match the Project
        if self.project and not self.organization:
            self.organization = self.project.organization
        
        # 2. Validation: Ensure they match even if both were provided manually
        if self.organization != self.project.organization:
            raise ValueError("Task organization must match the Project's organization.")


        super().save(*args, **kwargs)
        self.project.update_status()

    def __str__(self):
        return self.title

