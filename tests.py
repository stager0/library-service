from datetime import datetime

from django.utils import timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


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
        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.make_aware(datetime(2025, 10, 10, 10, 10, 10)),
            expected_return_date=timezone.make_aware(datetime(2025, 10, 11, 10, 10, 10)),
            pay_status="PAID",
            book=self.book,
            user=self.user
        ),
        self.borrowing1 = Borrowing.objects.create(
            borrow_date=timezone.make_aware(datetime(2030, 10, 10, 10, 10, 10)),
            expected_return_date=timezone.make_aware(datetime(2030, 10, 11, 10, 10, 10)),
            pay_status="PAID",
            book=self.book1,
            user=self.superuser
        ),
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


class BorrowingsApiTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("borrowings:borrowing-list")

        self.borrowing_data = {
            "borrow_date": timezone.make_aware(datetime(2100, 10, 10, 10, 10, 10)),
            "expected_return_date": timezone.make_aware(datetime(2100, 10, 11, 10, 10, 10)),
            "pay_status": "PAID",
            "book": self.book.id
        }
        self.detail_url = reverse("borrowings:borrowing-detail", kwargs={"pk": 1})

    def test_if_user_gets_only_his_borrowings_and_contains_his_borrowing_status_200(self):
        response = self.client.get(self.list_url)

        users_borrowing = Borrowing.objects.filter(user=self.user.id)
        serializer = BorrowingSerializer(users_borrowing, many=True)
        borrowing = Borrowing.objects.get(user=self.user.id)
        borrowing1 = Borrowing.objects.get(user=self.superuser.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)
        self.assertContains(response, borrowing.expected_return_date.isoformat().replace("+00:00", "Z"))
        self.assertContains(response, borrowing.borrow_date.isoformat().replace("+00:00", "Z"))
        self.assertNotContains(response, borrowing1.expected_return_date.isoformat().replace("+00:00", "Z"))
        self.assertNotContains(response, borrowing1.borrow_date.isoformat().replace("+00:00", "Z"))

    def test_borrowing_method_str_is_correct(self):
        borrowing = Borrowing.objects.first()

        self.assertEqual(str(borrowing), f"{borrowing.book.title} {borrowing.book.author}")

    def test_create_borrowing_if_user_is_unauthorized_status_401(self):
        self.client.logout()
        response = self.client.post(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_when_user_is_authorized_status_201(self):
        response = self.client.post(self.list_url, data=self.borrowing_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_if_anonymous_user_enters_status_401(self):
        self.client.logout()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_anonymous_user_tries_to_create_borrowing_status_401(self):
        self.client.logout()
        response = self.client.post(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_borrowing_if_is_staff_false_status_204(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_borrowing_without_data_status_400(self):
        data = {
            "borrow_date": "",
            "expected_return_date": "",
            "actual_return_date": "",
            "pay_status": "",
            "book": ""
        }
        response = self.client.post(self.list_url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_book_if_is_staff_false_status_200(self):
        response = self.client.patch(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_return_book_is_staff_false_status_403(self):
        return_url = reverse("borrowings:return-book", kwargs={"pk": 2})
        response = self.client.post(return_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("https://", response.data)

    def test_return_book_if_is_staff_true_status_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.super_access)
        return_url = reverse("borrowings:return-book", kwargs={"pk": 2})
        response = self.client.post(return_url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("checkout_fine_url", response.data)

    def test_return_book_if_user_is_anonymous_status_401(self):
        self.client.logout()

        response = self.client.post(self.list_url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

