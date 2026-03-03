from django.test import TestCase
from django.db import IntegrityError
from .models import Organization

class OrganizationModelTest(TestCase):

    def setUp(self):
        """Create a base organization for tests"""
        self.org = Organization.objects.create(
            name="Community Organization Unit",
            slug="cou"
        )

    def test_organization_creation(self):
        """Verify the organization fields are saved correctly"""
        self.assertEqual(self.org.name, "Community Organization Unit")
        self.assertEqual(self.org.slug, "cou")
        self.assertIsNotNone(self.org.created_at)

    def test_string_representation(self):
        """Verify the __str__ method returns the name"""
        self.assertEqual(str(self.org), self.org.name)

    def test_slug_uniqueness(self):
        """Verify that creating a duplicate slug raises an IntegrityError"""
        # Attempt to create another org with the same slug 'cou'
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                name="Another Org",
                slug="cou"
            )