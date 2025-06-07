from rest_framework import serializers

from borrowings.models import Borrowing
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "borrowing_id", "session_url", "session_id", "money_to_pay")
        read_only_fields = ("id",)


class CreatePaymentSessionSerializer(serializers.Serializer):
    money_to_pay = serializers.DecimalField(max_digits=8, decimal_places=2)
    borrowing_id = serializers.IntegerField()

    def validate_borrowing_id(self, value):
        if not Borrowing.objects.filter(id=value).exists():
            raise serializers.ValidationError("Borrowing with given id not exists.")
        return value
