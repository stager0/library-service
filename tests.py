from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Book
from books.serializers import BookSerializer
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
            daily_fee=1.00
        )
        self.book1 = Book.objects.create(
            title="Kolobok",
            author="Lesya Ukrainka",
            cover="SOFT",
            inventory=3,
            daily_fee=1.00
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.super_refresh = RefreshToken.for_user(self.superuser)
        self.access_token = str(self.refresh.access_token)
        self.super_access = str(self.super_refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)


class BookApiTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("books:book-list")
        self.detail_url = reverse("books:book-detail", kwargs={"pk": 1})

    def test_if_list_returns_all_books_and_contains_the_right_data(self):
        response = self.client.get(self.list_url)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(serializer.data, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book1.title)

    def test_book_str(self):
        book = Book.objects.first()

        self.assertEqual(str(book), f"Title: {self.book.title}, Author: {self.book.author}, Daily Fee {self.book.daily_fee}")

    def test_create_book_with_is_staff_false_status_403(self):
        response = self.client.post(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_with_is_staff_true_status_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.super_access)
        create_data={
            "title": "Test",
            "author": "Test",
            "cover": "Hard",
            "inventory": 233,
            "daily_fee": 1.99
        }
        response = self.client.post(self.list_url, data=create_data, format="json")
        books_count = Book.objects.all().count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(books_count, 3)

    def test_if_anonymous_user_enters_status_200(self):
        self.client.logout()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book.title)

    def test_if_anonymous_user_tries_to_create_book_status_401(self):
        self.client.logout()
        response = self.client.post(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_if_is_staff_false_status_403(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_without_data_status_400(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.super_access)
        data = {
            "title": "",
            "author": "",
            "cover": "",
            "inventory": "",
            "daily_fee": ""
        }
        response = self.client.post(self.list_url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_anonymous_user_tries_to_delete_book_status_401(self):
        self.client.logout()
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_book_if_is_staff_false_status_403(self):
        response = self.client.patch(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BorrowingsApiTests(TestCase):
    pass