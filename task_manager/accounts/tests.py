from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization # Adjust path if needed

User = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        """Set up a sample organization for the user tests"""
        self.org = Organization.objects.create(name="COU")

    def test_create_user_with_role_and_org(self):
        """Test that a user is created with the correct role and organization"""
        user = User.objects.create_user(
            username="test_manager",
            password="password123",
            organization=self.org,
            role="OWNER"
        )
        
        self.assertEqual(user.username, "test_manager")
        self.assertEqual(user.role, "OWNER")
        self.assertEqual(user.organization.name, "COU")
        self.assertEqual(str(user), "test_manager") # Tests the __str__ method

    def test_user_default_flags(self):
        """Test that default boolean flags are set correctly on creation"""
        user = User.objects.create_user(
            username="new_user",
            password="password123"
        )
        
        # Verify defaults
        self.assertFalse(user.must_change_password)
        self.assertFalse(user.email_verified)

    def test_blank_fields_allowed(self):
        """Test that role and organization can be null/blank as defined in model"""
        user = User.objects.create_user(
            username="freelancer",
            password="password123"
        )
        
        self.assertIsNone(user.organization)
        self.assertIsNone(user.role)

    def test_username_uniqueness(self):
        """Test that creating a duplicate username raises an error"""
        User.objects.create_user(username="unique_user", password="password123")
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="unique_user", password="password456")


