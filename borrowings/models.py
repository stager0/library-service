from django.db import models
from django.utils import timezone

from books.models import Book
from users.models import User


class Borrowing(models.Model):
    class PayStatusChoices(models.TextChoices):
        PAID = "Paid"
        PENDING = "Pending"

    borrow_date = models.DateTimeField(default=timezone.now, blank=True)
    expected_return_date = models.DateTimeField(blank=True, null=True)
    actual_return_date = models.DateTimeField(blank=True, null=True)
    pay_status = models.CharField(
        null=True,
        blank=True,
        max_length=55,
        choices=PayStatusChoices,
        default="PENDING"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
