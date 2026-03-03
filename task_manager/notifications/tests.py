from django.test import TestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization
from .models import Notification

User = get_user_model()

class NotificationModelTest(TestCase):

    def setUp(self):
        """Setup an organization and a recipient user"""
        self.org = Organization.objects.create(name="COU", slug="cou")
        self.user = User.objects.create_user(username="recipient_user", password="password123")

    def test_notification_creation_and_defaults(self):
        """Verify notification saves correctly with default is_read=False"""
        note = Notification.objects.create(
            organization=self.org,
            recipient=self.user,
            message="You have a new task assigned."
        )

        self.assertEqual(note.message, "You have a new task assigned.")
        self.assertFalse(note.is_read)  # Verify default value
        self.assertEqual(note.recipient, self.user)
        self.assertIsNotNone(note.created_at)

    def test_notification_ordering(self):
        """Verify notifications appear newest first (Inbox style)"""
        Notification.objects.create(organization=self.org, recipient=self.user, message="Oldest")
        Notification.objects.create(organization=self.org, recipient=self.user, message="Newest")

        notifications = Notification.objects.filter(recipient=self.user)
        # With ordering = ["-created_at"], 'Newest' should be index 0
        self.assertEqual(notifications[0].message, "Newest")

    def test_mark_as_read(self):
        """Verify that updating is_read functions correctly"""
        note = Notification.objects.create(
            organization=self.org,
            recipient=self.user,
            message="Read this."
        )
        
        note.is_read = True
        note.save()
        
        refresh_note = Notification.objects.get(id=note.id)
        self.assertTrue(refresh_note.is_read)

    def test_cascade_deletion(self):
        """Verify that deleting a user removes their notifications"""
        Notification.objects.create(organization=self.org, recipient=self.user, message="Bye")
        
        user_id = self.user.id
        self.user.delete()
        
        # Check that notifications for this user are gone
        self.assertEqual(Notification.objects.filter(recipient_id=user_id).count(), 0)