from rest_framework import viewsets

from activities.models import News
from activities.serializers import NewsSerializer


class Activity:
    pass


class NewsViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с новостями.
    """
    serializer_class = NewsSerializer
    queryset = News.objects.all()
