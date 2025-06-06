from django.db import transaction
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from telegram_bot.models import UserProfile
from telegram_bot.views import send_message


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingReadSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date",)
        read_only_fields = ("id",)


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
        data = \
            f"Book Title: {book.title}\n" \
            f"Book Author: {book.author}\n" \
            f"Expected return date: {borrowing.expected_return_date}\n" \
            f"Price per day: {book.daily_fee}\n"

        email = user.email
        profile_chat_id = UserProfile.objects.get(email=email).telegram_chat_id

        send_message(chat_id=profile_chat_id, text=f"You have new borrowing:\n{data}")

        return borrowing
