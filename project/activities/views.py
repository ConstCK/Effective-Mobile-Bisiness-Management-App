from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from activities.models import News
from activities.serializers import NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с новостями.
    Доступно только администраторам.
    """
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    permission_classes = [IsAdminUser]

    def create(self, request: Request, *args, **kwargs) -> Response:
