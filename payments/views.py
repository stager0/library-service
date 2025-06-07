import os

import stripe
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    CreatePaymentSessionSerializer
)
from telegram_bot.models import UserProfile
from telegram_bot.views import send_message

FINE_MULTIPLIER = 2
SUCCESS_URL=f"https://{os.getenv('WEBHOOK_WITHOUT_PROTOCOL_AND_PATH')}/api/payments/success-pay/?session_id="
CANCEL_URL=f"https://{os.getenv('WEBHOOK_WITHOUT_PROTOCOL_AND_PATH')}/api/payments/cancel-pay/"

load_dotenv()
stripe.api_key = os.getenv("STRIPE_PRIVATE_KEY")

class PaymentView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            borrowings_ids = Borrowing.objects.filter(user=self.request.user.id).values_list("id", flat=True)
            return queryset.filter(borrowing_id__in=borrowings_ids)

        if self.request.user.is_staff:
            return queryset

    def get(self, request, *args, **kwargs):
        if not "pk" in kwargs:
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)


def create_checkout_session(borrowing_id: int):
    borrowing_obj = Borrowing.objects.get(id=borrowing_id)
    money_to_pay = (borrowing_obj.expected_return_date - borrowing_obj.borrow_date).days * borrowing_obj.book.daily_fee
    amount_in_cents = int(money_to_pay * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": borrowing_obj.book.title
                },
                "unit_amount": amount_in_cents,
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=SUCCESS_URL + "{CHECKOUT_SESSION_ID}",
        cancel_url=CANCEL_URL
    )
    Payment.objects.create(
        type="PAYMENT",
        borrowing_id=borrowing_id,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=money_to_pay
    )
    return session

def create_fine_checkout_session(borrowing_id: int, count_of_delay_days: int):
    borrowing_obj = Borrowing.objects.get(id=borrowing_id)
    overdue_fine = (count_of_delay_days * borrowing_obj.book.daily_fee) * FINE_MULTIPLIER
    overdue_fine_in_cents = int(overdue_fine * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Fine of overdue days for book: '{borrowing_obj.book.title}'\n "
                            f"Count of overdue days: {count_of_delay_days}"
                },
                "unit_amount": overdue_fine_in_cents
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=SUCCESS_URL + "{CHECKOUT_SESSION_ID}",
        cancel_url=CANCEL_URL
    )
    Payment.objects.create(
        type="FINE",
        borrowing_id=borrowing_id,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=overdue_fine
    )
    return session


class CreateCheckoutSessionView(APIView):
    def post(self, request):
        serializer = CreatePaymentSessionSerializer(data=request.data)

        if serializer.is_valid():
            borrowing_id = serializer.validated_data["borrowing_id"]

            checkout_session = create_checkout_session(borrowing_id)

            return Response({"checkout_url": checkout_session.session.url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
