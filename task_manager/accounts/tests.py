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


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from unittest.mock import patch
from rest_framework import serializers
from organizations.models import Organization
from .serializers import RegisterSerializer

User = get_user_model()

class RegisterSerializerTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "username": "founder_mark",
            "email": "mark@startup.com",
            "password": "SecurePassword123",
            "password_confirmation": "SecurePassword123",
            "organization_name": "Mark Ventures"
        }
        # Mocking request for the serializer context
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        self.request = factory.get('/')

    def test_registration_success(self):
        """Verify user and organization are created together"""
        # We patch the email function so it doesn't actually send during the test
        with patch('accounts.serializers.send_verification_email') as mock_email:
            serializer = RegisterSerializer(data=self.valid_data, context={'request': self.request})
            self.assertTrue(serializer.is_valid())
            user = serializer.save()

            # 1. Verify User creation
            self.assertEqual(user.username, "founder_mark")
            self.assertEqual(user.role, "OWNER")
            self.assertFalse(user.is_active)  # Check the 'IMPORTANT' flag

            # 2. Verify Organization creation
            self.assertIsNotNone(user.organization)
            self.assertEqual(user.organization.name, "Mark Ventures")
            self.assertTrue(user.organization.slug.startswith("mark-ventures-"))

            # 3. Verify email was triggered
            mock_email.assert_called_once()

    def test_password_mismatch(self):
        """Verify validation fails if passwords don't match"""
        invalid_data = self.valid_data.copy()
        invalid_data['password_confirmation'] = "WrongPassword"
        
        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], "Password fields didn't match.")

    def test_transaction_atomic_rollback(self):
        """Verify that if User creation fails, the Organization is not created"""
        # We force a failure by providing an existing username
        User.objects.create_user(username="founder_mark", email="old@email.com")
        
        serializer = RegisterSerializer(data=self.valid_data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        
        # This should fail during .save() because of duplicate username
        with self.assertRaises(Exception):
            serializer.save()

        # Because of transaction.atomic(), the organization should not exist
        self.assertFalse(Organization.objects.filter(name="Mark Ventures").exists())