from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.permissions import IsAdminOrAllowAnyReadOnly
from borrowings.serializers import BorrowingSerializer, BorrowingReadSerializer


# Create your views here.
class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView
    ):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrAllowAnyReadOnly,)

    def get_serializer_class(self):
        if self.request.method == "GET" and "pk" in self.kwargs:
            return BorrowingReadSerializer
        return BorrowingSerializer
