"""
Test Model function
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

from decimal import Decimal


def sample_user(email='user@example.com', password='testpass123'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Tests for models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email successful"""
        email = 'user@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email new user os normalized."""
        email = 'user@EXAMPLE.COM'
        user = get_user_model().objects.create_user(
            email,
            'test123',
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_is_valid_email(self):
        """Test creating a user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                'test123',
            )

    def test_create_new_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email='user@example.com',
            password='test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan tag',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the ingredient string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Sample recipe',
            time_minutes=5,
            price=Decimal('5.25')
        )

        self.assertEqual(str(recipe), recipe.title)
