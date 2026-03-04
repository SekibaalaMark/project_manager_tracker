from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization # Adjust path if needed
from .serializers import *

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




from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .serializers import LoginSerializer

User = get_user_model()

class LoginSerializerTest(TestCase):

    def setUp(self):
        self.password = "SecurePassword123"
        self.user = User.objects.create_user(
            username="mark_manager",
            password=self.password,
            email_verified=True,
            is_active=True,
            role="MEMBER"
        )

    def test_login_success(self):
        """Verify successful login returns user and JWT tokens"""
        data = {"username": "mark_manager", "password": self.password}
        serializer = LoginSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        
        self.assertIn("access", validated_data)
        self.assertIn("refresh", validated_data)
        self.assertEqual(validated_data["user"], self.user)

    def test_login_invalid_credentials(self):
        """Verify failure with wrong password"""
        data = {"username": "mark_manager", "password": "wrongpassword"}
        serializer = LoginSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "Invalid username or password.")

    def test_login_inactive_user(self):
        """Verify failure for disabled accounts"""
        self.user.is_active = False
        self.user.save()
        
        data = {"username": "mark_manager", "password": self.password}
        serializer = LoginSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "User account is disabled.")

    def test_owner_email_verification_required(self):
        """Verify that Owners cannot login without email verification"""
        owner = User.objects.create_user(
            username="owner_user",
            password=self.password,
            role="OWNER",
            email_verified=False,
            is_active=True
        )
        
        data = {"username": "owner_user", "password": self.password}
        serializer = LoginSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "Please verify your email first.")





from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.test import APIRequestFactory
from organizations.models import Organization
from .serializers import CreateOrganizationUserSerializer

User = get_user_model()

class CreateOrganizationUserSerializerTest(TestCase):

    def setUp(self):
        self.org = Organization.objects.create(name="Tech Corp", slug="tech-corp")
        self.owner = User.objects.create_user(
            username="owner_mark", 
            role="OWNER", 
            organization=self.org
        )
        self.member = User.objects.create_user(
            username="member_joe", 
            role="MEMBER", 
            organization=self.org
        )
        self.factory = APIRequestFactory()

    @patch('accounts.serializers.send_temporary_password_email')
    def test_create_user_success_by_owner(self, mock_email):
        """Verify OWNER can create a user within their own organization"""
        request = self.factory.post('/')
        request.user = self.owner # Set request user as OWNER
        
        data = {
            "email": "new_staff@tech.com",
            "username": "new_staff",
            "role": "MANAGER"
        }
        
        serializer = CreateOrganizationUserSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        new_user = serializer.save()

        # Check user details
        self.assertEqual(new_user.organization, self.org)
        self.assertEqual(new_user.role, "MANAGER")
        self.assertTrue(new_user.must_change_password)
        
        # Verify email with temp password was triggered
        mock_email.assert_called_once()
        # Verify the password passed to email is an 8-character string
        self.assertEqual(len(mock_email.call_args[0][1]), 8)

    def test_create_user_forbidden_for_member(self):
        """Verify non-OWNERs are blocked from creating users"""
        request = self.factory.post('/')
        request.user = self.member # Set request user as MEMBER
        
        data = {"email": "test@test.com", "username": "test", "role": "MEMBER"}
        serializer = CreateOrganizationUserSerializer(data=data, context={'request': request})
        
        # Should fail validation
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "Only OWNER can create users.")







class SetNewPasswordSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="new_staff",
            password="temp_password123",
            must_change_password=True
        )
        self.factory = APIRequestFactory()

    def test_set_password_success(self):
        """Verify password is changed and flag is cleared"""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            "new_password": "NewSecurePassword123",
            "confirm_new_password": "NewSecurePassword123"
        }
        
        serializer = SetNewPasswordSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # 1. Verify the flag is now False
        self.assertFalse(user.must_change_password)
        
        # 2. Verify the new password actually works for authentication
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(username="new_staff", password="NewSecurePassword123")
        self.assertIsNotNone(authenticated_user)

    def test_password_too_short(self):
        """Verify the 6-character minimum length constraint"""
        data = {"new_password": "123", "confirm_new_password": "123"}
        serializer = SetNewPasswordSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors['non_field_errors'][0], "Password too short.")

    def test_passwords_mismatch(self):
        """Verify validation fails if confirm field is different"""
        data = {
            "new_password": "password123",
            "confirm_new_password": "different_password"
        }
        serializer = SetNewPasswordSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "Passwords do not match.")






from unittest.mock import patch
from rest_framework.test import APIRequestFactory

class ResendVerificationSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="unverified_user",
            email="test@example.com",
            password="password123",
            email_verified=False
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/')

    @patch('accounts.serializers.send_verification_email')
    def test_resend_success(self, mock_email):
        """Verify email is resent to an unverified user"""
        data = {"email": "test@example.com"}
        serializer = ResendVerificationSerializer(data=data, context={'request': self.request})
        
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        # Check that the email function was called once
        mock_email.assert_called_once_with(self.request, self.user)

    def test_resend_already_verified(self):
        """Verify error if user is already verified"""
        self.user.email_verified = True
        self.user.save()
        
        data = {"email": "test@example.com"}
        serializer = ResendVerificationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "Email is already verified.")

    def test_resend_user_not_found(self):
        """Verify error if email doesn't exist in system"""
        data = {"email": "nonexistent@example.com"}
        serializer = ResendVerificationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "User with this email does not exist.")




from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.test import APIRequestFactory
from .serializers import ChangePasswordSerializer

User = get_user_model()

class ChangePasswordSerializerTest(TestCase):

    def setUp(self):
        self.old_password = "OldSecurePassword123"
        self.user = User.objects.create_user(
            username="testuser",
            password=self.old_password
        )
        self.factory = APIRequestFactory()

    def test_change_password_success(self):
        """Verify password update works with correct current password"""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            "current_password": self.old_password,
            "new_password": "NewDifferentPassword456!",
            "confirm_password": "NewDifferentPassword456!"
        }
        
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Verify password actually changed in DB
        self.assertTrue(user.check_password("NewDifferentPassword456!"))
        self.assertFalse(user.check_password(self.old_password))

    def test_incorrect_current_password(self):
        """Verify validation fails if the current password is wrong"""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            "current_password": "WrongCurrentPassword",
            "new_password": "NewPassword123",
            "confirm_password": "NewPassword123"
        }
        
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("current_password", serializer.errors)
        self.assertEqual(serializer.errors["current_password"][0], "Current password is incorrect.")

    def test_new_passwords_mismatch(self):
        """Verify validation fails if confirmation doesn't match"""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            "current_password": self.old_password,
            "new_password": "NewPassword123",
            "confirm_password": "MismatchPassword456"
        }
        
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)





class ForgotPasswordSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="forgetful_user",
            email="lost@example.com",
            password="OldPassword123",
            must_change_password=False
        )

    @patch('accounts.serializers.send_temporary_password_email')
    def test_forgot_password_success(self, mock_email):
        """Verify password reset generates new password and sets flag"""
        data = {"email": "lost@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # 1. Verify the 'must_change_password' flag is now True
        self.assertTrue(user.must_change_password)
        
        # 2. Verify the old password no longer works
        self.assertFalse(user.check_password("OldPassword123"))
        
        # 3. Verify email was sent with an 8-character string
        mock_email.assert_called_once()
        temp_pass = mock_email.call_args[0][1]
        self.assertEqual(len(temp_pass), 8)
        
        # 4. Verify the new temp password actually works
        self.assertTrue(user.check_password(temp_pass))

    def test_forgot_password_email_not_found(self):
        """Verify validation error when email doesn't exist"""
        data = {"email": "unknown@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(serializer.errors["email"][0], "No user found with this email.")





from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from organizations.models import *



class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('register') # Ensure this matches the name in your urls.py
        self.valid_payload = {
            "username": "founder_mark",
            "email": "mark@startup.com",
            "password": "SecurePassword123",
            "password_confirmation": "SecurePassword123",
            "organization_name": "Mark Ventures"
        }

    @patch('accounts.serializers.send_verification_email')
    def test_register_user_success(self, mock_email):
        """Test successful registration via the API endpoint"""
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check response message
        self.assertEqual(response.data["message"], "User registered successfully")
        
        # Verify database changes
        self.assertTrue(User.objects.filter(username="founder_mark").exists())
        self.assertTrue(Organization.objects.filter(name="Mark Ventures").exists())

    def test_register_invalid_data(self):
        """Test that invalid data returns 400 Bad Request"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['password_confirmation'] = "Mismatch"
        
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify no user was created
        self.assertFalse(User.objects.filter(username="founder_mark").exists())

    @patch('accounts.serializers.send_verification_email')
    def test_register_duplicate_username(self, mock_email):
        """Test that registering an existing username fails"""
        # Create user first
        User.objects.create_user(username="founder_mark", email="other@test.com", password="password")
        
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)