from django.urls import include, path
from rest_framework.routers import DefaultRouter

from books.views import BookViewSet


app_name = "books"

router = DefaultRouter()

router.register("book", BookViewSet)

urlpatterns= [
    path("", include(router.urls))
]