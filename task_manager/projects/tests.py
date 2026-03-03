from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from organizations.models import Organization
from .models import Project, Task # Assuming Task is in the same apps' models

User = get_user_model()

class ProjectModelTest(TestCase):

    def setUp(self):
        self.org = Organization.objects.create(name="COU", slug="cou")
        self.user = User.objects.create_user(username="pm_mark", email="mark@cou.com")
        self.project = Project.objects.create(
            name="Alpha Project",
            organization=self.org,
            created_by=self.user,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=10)
        )

    def test_project_duration(self):
        """Test the @property project_duration"""
        self.assertEqual(self.project.project_duration, 10)

    def test_is_project_overdue(self):
        """Test @property is_project_overdue logic"""
        # Set end_date to yesterday
        self.project.end_date = timezone.now().date() - timedelta(days=1)
        self.project.status = "IN_PROGRESS"
        self.assertTrue(self.project.is_project_overdue)
        
        # If completed, it shouldn't be overdue even if date passed
        self.project.status = "COMPLETED"
        self.assertFalse(self.project.is_project_overdue)

    @patch('projects.models.send_Project_completion_email')
    def test_update_status_to_completed(self, mock_email):
        """Test that project moves to COMPLETED and sends email when all tasks are done"""
        # Create completed tasks
        Task.objects.create(
            title="Task 1", project=self.project, 
            status="COMPLETED", assigned_to=self.user,
            start_date=timezone.now().date(), end_date=timezone.now().date()
        )
        
        self.project.update_status()
        
        self.assertEqual(self.project.status, "COMPLETED")
        # Verify the email function was called
        mock_email.assert_called_once_with(self.user, self.project)

    def test_update_status_in_progress(self):
        """Test project moves to IN_PROGRESS if at least one task is not PENDING"""
        Task.objects.create(
            title="Task 1", project=self.project, 
            status="IN_PROGRESS", assigned_to=self.user,
            start_date=timezone.now().date(), end_date=timezone.now().date()
        )
        
        self.project.update_status()
        self.assertEqual(self.project.status, "IN_PROGRESS")