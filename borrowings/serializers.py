from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.views import create_checkout_session
from telegram_bot.models import UserProfile
from telegram_bot.views import send_message


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user", "pay_status")
        read_only_fields = ("id", "pay_status", "user")


class BorrowingReadSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date",)
        read_only_fields = ("id",)


class BorrowingCreateSerializer(BorrowingSerializer):
    checkout_session = serializers.SerializerMethodField(required=False, allow_null=True)
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "checkout_session", "book", "pay_status")
        read_only_fields = ("id", "pay_status")

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

    @extend_schema_field(str)
    def get_checkout_session(self, obj):
        return create_checkout_session(obj.pk).url

    def validate_expected_return_date(self, value):
        if value:
            return value
        raise serializers.ValidationError("Expected return date must be provided!")
