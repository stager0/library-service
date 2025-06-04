from rest_framework import mixins
from rest_framework.generics import GenericAPIView

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingReadSerializer


class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET" and "pk" in self.kwargs:
            return BorrowingReadSerializer
        return BorrowingSerializer

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
