from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter, extend_schema_view
from rest_framework import status, viewsets
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


class BorrowingView(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET" and "pk" in self.kwargs and not "return-book" in self.kwargs:
            return BorrowingReadSerializer
        if self.request.method == "PATCH":
            return BorrowingSerializer
        if self.request.method == "POST" and "pk" in self.kwargs:
            return BorrowingSerializer
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

    @extend_schema(
        summary="Get a list of all Borrowings",
        description="Return a list of all Borrowings what belong to request user (if user is admin, it returns all borrowings)",
        tags=["borrowing"],
        request=BorrowingSerializer(many=True),
        responses={
            200: BorrowingSerializer(many=True),
        },
        parameters=[
            OpenApiParameter(
                "Is active",
                type=str,
                description="Filter Borrowings by is_active (/?is_active=[choices: '1', 'true', 'yes', 'active'])",
                required=False
            ),
            OpenApiParameter(
                "Isn't Active",
                type=str,
                description="Filter Borrowings by is_active  (/?is_active=[choices: '0', 'false', 'no', 'inactive'])",
                required=False
            ),
            OpenApiParameter(
                "User Id",
                type=int,
                description="Filter Borrowings by user_id",
                required=False
            )
        ],
        examples=[
            OpenApiExample(
                "application/json",
                value=
                {
                    "id": 2,
                    "borrow_date": "2025-06-05T14:31:00Z",
                    "expected_return_date": "2025-06-14T14:29:00Z",
                    "actual_return_date": "2025-06-05T12:32:09.754208Z",
                    "book": 1,
                    "user": 2,
                    "pay_status": "PAID"
                },
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new Borrowing",
        description="This endpoint allow you create a new Borrowing with provided data",
        tags=["borrowing"],
        request=BorrowingCreateSerializer,
        responses={
            201: BorrowingCreateSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Not Expected Return Date",
                        value=[
                            {
                                "expected_return_date": [
                                    "Expected return date must be provided!"
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
                    "expected_return_date": "2025-12-12 00:00:00"
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Get a Borrowing by ID ",
        description="Retrieve a Borrowing by given ID",
        tags=["borrowing"],
        request=BorrowingReadSerializer,
        responses={
            200: BorrowingReadSerializer(),
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Not Found"),
        },
        examples=[
            OpenApiExample(
                "application/json",
                value=[
                    {
                        "id": 2,
                        "borrow_date": "2025-06-05T14:31:00Z",
                        "expected_return_date": "2025-06-14T14:29:00Z",
                        "actual_return_date": "2025-06-05T12:32:09.754208Z",
                        "book": {
                            "id": 1,
                            "title": "Kobzar",
                            "author": "Taras",
                            "cover": "Hard",
                            "inventory": 13,
                            "daily_fee": "12.00"
                        },
                        "user": 2,
                        "pay_status": "PAID"
                    },
                ]
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a Borrowing",
        description="Update a Borrowing by given ID",
        tags=["borrowing"],
        request=BorrowingSerializer,
        responses={
            200: BorrowingSerializer(),
            404: OpenApiResponse(description="Not Found"),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Not Expected Return Date Provided",
                        value=[
                            {
                                "expected_return_date": [
                                    "Expected return date must be provided!"
                                ]
                            }
                        ]
                    )
                ]
            ),
        },
        examples=[
            OpenApiExample(
                "application/json",
                value={
                    "id": 1,
                    "title": "Kobzar",
                    "author": "Taras",
                    "cover": "Hard",
                    "inventory": 13,
                    "daily_fee": "12.00"
                }
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


    @extend_schema(
        summary="Delete a borrowing",
        description="Destroy a borrowing by given ID",
        tags=["borrowing"],
        request=BorrowingSerializer,
        responses={
            204: OpenApiResponse(description="No Content"),
            404: OpenApiResponse(description="Book Not Found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Partially updates the borrowing",
        description="It partially updates the borrowing by given id and data (only for admins)",
        tags=["borrowing"],
        request=BorrowingSerializer,
        responses={
            200: BorrowingSerializer(),
            404: OpenApiResponse(description="Not Found"),
            400: OpenApiResponse(description="Bad Request")
        },
        examples=[
            OpenApiExample(
                "Partial Update",
                value={
                    "expected_return_date": "2025-09-09 09:00:00"
                }
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().partial_update(request, *args, **kwargs)


class BorrowingReturnView(APIView):
    permission_classes = [IsAdminUser, ]

    @extend_schema(
        summary="Return Book",
        description="Returns book and checks if the fine must be pay. "
                    "Returns a pay link to Stripe and in case successfully "
                    "payment will notice it ti the DataBase",
        tags=["borrowing"],
        request=BorrowingReturnSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                examples=[
                    OpenApiExample(
                        "Returns payment-link",
                        value=[
                            {
                                "checkout_fine_url": "https://checkout.stripe.com/c/pay/cs_test_arZ2FcXdwYHgl......"
                            }
                        ]
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Non-existent ID was given",
                        value=[
                            {
                                "message": "Borrowing with given ID not exists"
                            }
                        ]
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "It takes id from query and needs nothing, only an empty dict",
                value=[
                    "{}"
                ]
            )
        ]

    )
    def post(self, request, pk=None):
        if not pk:
            return Response({"detail": "Not pk provided"}, status.HTTP_400_BAD_REQUEST)

        borrowing_obj = None
        try:
            borrowing_obj = Borrowing.objects.get(pk=pk)
        except Borrowing.DoesNotExist:
            return Response({"message": "Borrowing with given ID not exists"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            book = Book.objects.get(pk=borrowing_obj.book.pk)
            return_date = request.data.get("actual_return_date")

            serializer = BorrowingReturnSerializer(data={"actual_return_date": return_date})
            if serializer.is_valid() and not borrowing_obj.actual_return_date and borrowing_obj:
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
