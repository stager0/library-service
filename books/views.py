from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrAllowAnyReadOnly
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrAllowAnyReadOnly, ]

    @extend_schema(
        summary="Create a new Book",
        description="This endpoint allow you create a new Book with provided data",
        tags=["book"],
        request=BookSerializer,
        responses={
            201: BookSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Not Data Provided",
                        value=[
                            {
                                "title": [
                                    "This field may not be blank."
                                ],
                                "author": [
                                    "This field may not be blank."
                                ],
                                "cover": [
                                    "This field may not be blank."
                                ],
                                "inventory": [
                                    "A valid integer is required."
                                ],
                                "daily_fee": [
                                    "A valid number is required."
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
                    "title": "Kobzar",
                    "author": "Taras Shevchenko",
                    "cover": "HARD",
                    "inventory": 458,
                    "daily_fee": 1.98
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Get a list of all Books",
        description="Return a list of all Book what are registered in the DataBase",
        tags=["book"],
        responses={
            200: BookSerializer(many=True),
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
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get a book by ID ",
        description="Retrieve a Book by given ID",
        tags=["book"],
        responses={
            200: BookSerializer(),
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Not Found"),
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
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a book",
        description="Update a book by given ID",
        tags=["book"],
        request=BookSerializer,
        responses={
            200: BookSerializer(),
            404: OpenApiResponse(description="Not Found"),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Not Data Provided",
                        value=[
                            {
                                "title": [
                                    "This field may not be blank."
                                ],
                                "author": [
                                    "This field may not be blank."
                                ],
                                "inventory": [
                                    "A valid integer is required."
                                ],
                                "daily_fee": [
                                    "A valid number is required."
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
        summary="Delete a book",
        description="Destroy a book by given ID",
        tags=["book"],
        request=BookSerializer,
        responses={
            204: OpenApiResponse(description="No Content"),
            404: OpenApiResponse(description="Book Not Found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Partially updates the book",
        description="It partially updates the book by given id and data (only for admins)",
        tags=["book"],
        request=BookSerializer,
        responses={
            200: BookSerializer(),
            404: OpenApiResponse(description="Not Found"),
            400: OpenApiResponse(description="Bad Request")
        },
        examples=[
            OpenApiExample(
                "Partial Update",
                value={
                    "inventory": 12,
                    "author": "Lesya Ukrainka"
                }
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
