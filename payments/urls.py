from django.urls import path

from payments.views import CreateCheckoutSessionView, PaymentView


app_name = "payments"

urlpatterns = [
    path("create-checkout-session/", CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("payment-list/", PaymentView.as_view(), name="payment_list"),
    path("payment-list/<int:pk>/", PaymentView.as_view(), name="payment_detail")
]