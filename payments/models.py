from django.db import models

class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=255, choices=StatusChoices, blank=True, null=True)
    type = models.CharField(max_length=255, choices=TypeChoices)
    borrowing_id = models.IntegerField()
    session_url = models.URLField(max_length=255)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=8)
