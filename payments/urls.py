from django.urls import path
from payments.views import CreateCheckoutSessionView, PaymentView, SuccessPayView, CancelPayView

app_name = "payments"

urlpatterns = [
    path("create-checkout-session/", CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("payment-list/", PaymentView.as_view(), name="payment_list"),
    path("payment/<int:pk>/", PaymentView.as_view(), name="payment_detail"),
    path("success-pay/", SuccessPayView.as_view(), name="success-pay"),
    path("cancel-pay/", CancelPayView.as_view(), name="cancel-pay")
]
