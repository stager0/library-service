import environ
import stripe
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
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

env = environ.Env()
environ.Env.read_env()

FINE_MULTIPLIER = 2
SUCCESS_URL = f"https://{env('WEBHOOK_WITHOUT_PROTOCOL_AND_PATH')}/api/payments/success-pay/?session_id="
CANCEL_URL = f"https://{env('WEBHOOK_WITHOUT_PROTOCOL_AND_PATH')}/api/payments/cancel-pay/"

stripe.api_key = env("STRIPE_PRIVATE_KEY")

class PaymentView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            borrowings_ids = Borrowing.objects.filter(user=self.request.user.id).values_list("id", flat=True)
            return queryset.filter(borrowing_id__in=borrowings_ids)

        if self.request.user.is_staff:
            return queryset

    @extend_schema(
        summary="Get a payment list",
        description="Get a list with all payments what current user had made",
        tags=["payment"],
        request={
            200: OpenApiResponse(
                description="OK",
                examples=[
                    OpenApiExample(
                        "Payment list",
                        value=[
                            {
                                "id": 1,
                                "status": "PAID",
                                "type": "PAYMENT",
                                "borrowing_id": 4,
                                "session_url": "https://checkout.stripe.com/c/pay/cs_test_a116zqnM4jsOz3v0aKso5pxKn7u1i7fhDq5duDJ3KRVFCuaqPBNiMqdieL#fidkdWxOYHwnPyd1blpxYHZxWjA0V11JPUpVMDdCPWhAXEdEV19TXDBIRjVjX0RUZ0syS1RpdkxXUXJcdG5wS1E8PFFGT3dkYnJOaWNpUm1gX1NzSlVuRE1GTUpSMGNndW02aWlHSHBHR1RdNTVSblJOfDQ9QicpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
                                "session_id": "cs_test_a116zqnM4jsOz3v0aKso5pxKn7u1i7fhDq5duDJ3KRVFCuaqPBNiMqdieL",
                                "money_to_pay": "10.00"
                            }
                        ]
                    )
                ]
            ),
        },
        operation_id="Get_Payments_List"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a payment by given ID",
        description="Retrieve a payment by given ID what current user had made",
        tags=["payment"],
        request={
            200: OpenApiResponse(
                description="OK",
                examples=[
                    OpenApiExample(
                        "Payment Retrieve",
                        value=[
                            {
                                "id": 1,
                                "status": "PAID",
                                "type": "PAYMENT",
                                "borrowing_id": 4,
                                "session_url": "https://checkout.stripe.com/c/pay/cs_test_a116zqnM4jsOz3v0aKso5pxKn7u1i7fhDq5duDJ3KRVFCuaqPBNiMqdieL#fidkdWxOYHwnPyd1blpxYHZxWjA0V11JPUpVMDdCPWhAXEdEV19TXDBIRjVjX0RUZ0syS1RpdkxXUXJcdG5wS1E8PFFGT3dkYnJOaWNpUm1gX1NzSlVuRE1GTUpSMGNndW02aWlHSHBHR1RdNTVSblJOfDQ9QicpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
                                "session_id": "cs_test_a116zqnM4jsOz3v0aKso5pxKn7u1i7fhDq5duDJ3KRVFCuaqPBNiMqdieL",
                                "money_to_pay": "10.00"
                            }
                        ]
                    )
                ]
            ),
        },
        operation_id="Get_Payment_By_ID"
    )
    def retrieve(self, request, *args, **kwargs):
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


def create_fine_checkout_session(borrowing_id: int, count_of_delay_days: int) -> stripe.checkout.Session:
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


class SuccessPayView(APIView):
    serializer_class = PaymentSerializer

    @extend_schema(
        summary="Success payment page",
        description="Return some info about payment like currency, amount etc.",
        tags=["payment"],
        request=PaymentSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                examples=[
                    OpenApiExample(
                        "Successfully payment",
                        value=[
                            {
                                "message": "Payment was successful!",
                                "session_id": "cs_test_a1zyGgt7YEEzBOCdX59tFWPztBDmYckPkeV8s9OIE0g6MNpZWSVkB8JXlm",
                                "payment_status": "paid",
                                "amount_paid": 480.0,
                                "currency": "usd"
                            }
                        ]
                    )
                ]
            ),
        },
        operation_id="Success_Payment"
    )
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")

        if session_id:
            session = stripe.checkout.Session.retrieve(session_id)
            payment = Payment.objects.get(session_id=session_id)
            borrowing = Borrowing.objects.get(pk=payment.borrowing_id)
            if session.payment_status == "paid":
                payment.status = "PAID"
                payment.save()
                if not payment.type == "FINE":
                    borrowing.pay_status = "PAID"
                    borrowing.save()
                user = get_user_model().objects.get(id=self.request.user.id)
                try:
                    user_profile = UserProfile.objects.get(email=user)
                    send_message(chat_id=user_profile.telegram_chat_id,
                                 text=f"You have successfully paid for the book: '{borrowing.book.title}'")
                except UserProfile.DoesNotExist:
                    pass

            return Response({
                "message": "Payment was successful!",
                "session_id": session.id,
                "payment_status": session.payment_status,
                "amount_paid": session.amount_total / 100,
                "currency": session.currency,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Session ID is missing"}, status=status.HTTP_400_BAD_REQUEST)


class CancelPayView(APIView):
    serializer_class = PaymentSerializer

    @extend_schema(
        summary="Get a cancel page",
        description="Return a list of all Book what are registered in the DataBase",
        tags=["payment"],
        responses={
            200: OpenApiResponse(description="message: Your order was canceled. Please try again"),
        },
        operation_id="Cancel_Payment"
    )
    def get(self, request, *args, **kwargs):
        user = get_user_model().objects.get(pk=self.request.user.pk)
        canceled_pay = Payment.objects.get(status="PENDING")
        borrowing = Borrowing.objects.get(pk=canceled_pay.pk)
        borrowing.actual_return_date = None
        canceled_pay.delete()
        borrowing.save()
        try:
            user_profile = UserProfile.objects.get(email=user)
            send_message(chat_id=user_profile.telegram_chat_id, text="You canceled the payment. Please try again...")
        except UserProfile.DoesNotExist:
            pass
        return Response({"message": "Your order was canceled. Please try again"}, status=status.HTTP_200_OK)


class CreateCheckoutSessionView(APIView):
    serializer_class = CreatePaymentSessionSerializer

    @extend_schema(
        summary="Create a new Checkout Session",
        description="This endpoint takes money_to_pay and borrowing_id and creates a new Checkout Session",
        tags=["payment"],
        request=CreatePaymentSessionSerializer,
        responses={
            201: CreatePaymentSessionSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Not Data Provided",
                        value=[
                            {
                                "money_to_pay": [
                                    "This field is required."
                                ],
                                "borrowing_id": [
                                    "This field is required."
                                ]
                            }
                        ]
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "application/json",
                value={
                    "money_to_pay": 18.00,
                    "borrowing_id": 3
                }
            )
        ],
        operation_id="Create_Payment_Session"
    )
    def post(self, request):
        serializer = CreatePaymentSessionSerializer(data=request.data)

        if serializer.is_valid():
            borrowing_id = serializer.validated_data["borrowing_id"]

            checkout_session = create_checkout_session(borrowing_id)

            return Response({"checkout_url": checkout_session.session.url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
