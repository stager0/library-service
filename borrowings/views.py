from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer
)
from payments.views import create_fine_checkout_session


class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericAPIView
):
    queryset = Borrowing.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET" and "pk" in self.kwargs and not "return-book" in self.kwargs:
            return BorrowingReadSerializer
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        elif self.request.user.is_staff:
            queryset = queryset.all()

        if is_active is not None:
            if is_active in ["1", "true", "yes", "active"]:
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active in ["0", "false", "no", "inactive"]:
                queryset = queryset.filter(actual_return_date__isnull=False)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset.distinct()

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BorrowingReturnView(APIView):
    permission_classes = [IsAdminUser,]

    def post(self, request, pk=None):
        if not pk:
            return Response({"detail": "Not pk provided"}, status.HTTP_400_BAD_REQUEST)

        borrowing_obj = Borrowing.objects.get(pk=pk)

        with transaction.atomic():
            book = Book.objects.get(pk=borrowing_obj.book.pk)
            return_date = request.data.get("actual_return_date")

            serializer = BorrowingReturnSerializer(data={"actual_return_date": return_date})
            if serializer.is_valid() and not borrowing_obj.actual_return_date and book.inventory > 0:
                borrowing_obj.actual_return_date = timezone.now()
                book.inventory += 1
                book.save()
                borrowing_obj.save()
                count_of_delay_days = (borrowing_obj.expected_return_date - timezone.now()).days
                if count_of_delay_days > 0:
                    session_fine = create_fine_checkout_session(
                        borrowing_id=borrowing_obj.id,
                        count_of_delay_days=count_of_delay_days
                    )
                    return Response({"checkout_fine_url": session_fine.url}, status=status.HTTP_200_OK)
                elif count_of_delay_days <= 0:
                    return Response({"message": "You don't have overdue!"}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
