from django.db import transaction
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingReadSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book")
        read_only_fields = ("id",)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)
        book = borrowing.book
        if book.inventory == 0:
            raise ValueError("There is no this book more")

        book.inventory -= 1
        book.save()
        borrowing.save()

        return borrowing
