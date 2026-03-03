from django.test import TestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization
from .models import ActivityLog

User = get_user_model()

class ActivityLogModelTest(TestCase):

    def setUp(self):
        """Set up environment for activity log testing"""
        self.org = Organization.objects.create(name="COU", slug="cou")
        self.user = User.objects.create_user(username="logger_user", password="password123")

    def test_activity_log_creation(self):
        """Verify an activity log can be created with metadata"""
        meta_data = {"project_id": 101, "ip_address": "192.168.1.1"}
        
        log = ActivityLog.objects.create(
            organization=self.org,
            user=self.user,
            action="CREATED_PROJECT",
            metadata=meta_data
        )

        self.assertEqual(log.action, "CREATED_PROJECT")
        self.assertEqual(log.metadata["project_id"], 101)
        self.assertEqual(str(log), f"{self.user.username} - CREATED_PROJECT")
        self.assertIsNotNone(log.timestamp)

    def test_activity_log_ordering(self):
        """Verify logs are ordered by timestamp descending (newest first)"""
        ActivityLog.objects.create(organization=self.org, user=self.user, action="First Action")
        ActivityLog.objects.create(organization=self.org, user=self.user, action="Second Action")
        
        logs = ActivityLog.objects.all()
        # The first log in the queryset should be the 'Second Action' due to ordering = ["-timestamp"]
        self.assertEqual(logs[0].action, "Second Action")

    def test_user_set_null_on_delete(self):
        """Verify that deleting a user doesn't delete the log (audit trail remains)"""
        log = ActivityLog.objects.create(
            organization=self.org,
            user=self.user,
            action="SENSITIVE_ACTION"
        )
        
        self.user.delete()
        log.refresh_from_db()
        
        self.assertIsNone(log.user) # on_delete=models.SET_NULL works
        self.assertEqual(log.action, "SENSITIVE_ACTION")