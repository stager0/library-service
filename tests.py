from django.test import TestCase
from rest_framework.test import APITestCase, APIClient

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Book
from borrowings.models import Borrowing


class BaseCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test_email@test.com",
            first_name="Vasyl",
            last_name="Muller",
            password="1qazcde3"
        )
        self.superuser = get_user_model().objects.create_superuser(
            email="test_email1@test.com",
            first_name="Oleg",
            last_name="Grynko",
            password="1qazcde3"
        )
        self.book = Book.objects.create(
            title="Kobzar",
            author="Taras Schevchenko",
            cover="HARD",
            inventory=3,
            dayly_fee=1.00
        )
        self.book1 = Book.objects.create(
            title="Kolobok",
            author="Lesya Ukrainka",
            cover="SOFT",
            inventory=3,
            dayly_fee=1.00
        )

        self.user = get_user_model().objects.create_user(email="test_user", password="1qazcde3")
        self.refresh = RefreshToken.for_user(self.user)
        self.super_refresh = RefreshToken.for_user(self.superuser)
        self.access = str(self.refresh.access_token)
        self.super_access = str(self.super_refresh.access_token)
        self.client = APIClient
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access)
