from django.db import models
from django.utils import timezone

from books.models import Book
from users.models import User


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    expected_return_date = models.DateTimeField(blank=True, null=True)
    actual_return_date = models.DateTimeField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
