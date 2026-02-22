from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Project(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    )

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "accounts.Organization",
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

        elif any(task.status != "PENDING" for task in tasks):
            self.status = "IN_PROGRESS"

        else:
            self.status = "PENDING"

        self.save(update_fields=["status"])

    def __str__(self):
        return self.name
    


