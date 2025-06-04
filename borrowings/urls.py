from django.urls import path

from borrowings.views import BorrowingView, BorrowingReturnView


app_name = "borrowings"
urlpatterns = [
    path("", BorrowingView.as_view(), name="borrowings-list"),
    path("<int:pk>/", BorrowingView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return-book/", BorrowingReturnView.as_view(), name="return-book")
]