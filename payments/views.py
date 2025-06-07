import os

import stripe
from dotenv import load_dotenv
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentSerializer

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


class CreateCheckoutSessionView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)

        if serializer.is_valid():
            money_to_pay = serializer.validated_data["money_to_pay"]
            borrowing_id = serializer.validated_data["borrowing_id"]
            borrowing_obj = Borrowing.objects.get(id=borrowing_id)

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": borrowing_obj.book.title
                        },
                        "unit_amount": money_to_pay,
                    },
                    "quantity": 1
                }],
                mode="payment"
            )
            return Response({"checkout_url": session.url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
