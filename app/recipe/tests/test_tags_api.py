from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URS = reverse('recipe:tag-list')


class PublicApiTests(TestCase):
    """Tests the public available api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTests(TestCase):
    """Test the authorized user api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URS)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Tests user get only authenticated user tags"""
        user2 = get_user_model().objects.create_user(
            'user2@gmail.com',
            'testpass123'
        )
        Tag.objects.create(user=user2, name='Fruit')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'test_tag'}
        self.client.post(TAGS_URS, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid_name(self):
        """Test creating a invalid tag raise error"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URS, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test retrieving tags assigned to recipe"""
        tag1 = Tag.objects.create(user=self.user, name='lunch')
        tag2 = Tag.objects.create(user=self.user, name='dinner')

        recipe = Recipe.objects.create(
            title='Chocolate cheeseecake',
            time_minutes=15,
            price=5.25,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URS, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_nique(self):
        """Test retrieve tags by assigned return unique value"""
        tag = Tag.objects.create(user=self.user, name='breakfast')
        Tag.objects.create(user=self.user, name='lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=24,
            price=5.55,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Coconut',
            time_minutes=2,
            price=5.15,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URS, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
