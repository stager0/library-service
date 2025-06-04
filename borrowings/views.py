from django.template.defaulttags import querystring
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingReadSerializer, BorrowingCreateSerializer


class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericAPIView
):
    queryset = Borrowing.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET" and "pk" in self.kwargs:
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
