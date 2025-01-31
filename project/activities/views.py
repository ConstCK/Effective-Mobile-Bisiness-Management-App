from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from activities.models import News, Meeting
from activities.serializers import NewsSerializer, MeetingSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с новостями.
    Доступно только администраторам.
    """
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    permission_classes = [IsAdminUser, ]

    # Создание новости
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            news = News(**serializer.validated_data)
            news.author = Profile.objects.get(user=request.user)
            news.save()
            result = self.serializer_class(news, many=False)
            return Response({'message': 'Успешное создания новости.',
                             'data': result.data},
                            status=status.HTTP_201_CREATED, )

        except Exception as error:
            return Response({'message': f'Ошибка создания новостей.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )


class MeetingViewSet(viewsets.ModelViewSet):
    """
    Класс для операций со встречами.
    Доступно только администраторам.
    """
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    permission_classes = [IsAdminUser, ]

    # Создание встречи
    def create(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            meeting = Meeting(**serializer.validated_data)
            meeting.organizer = Profile.objects.get(user=request.user)
            meeting.save()
            result = self.serializer_class(meeting, many=False)
            return Response({'message': 'Успешное создания новости.',
                             'data': result.data},
                            status=status.HTTP_201_CREATED, )

        except Exception as error:
            return Response({'message': f'Ошибка создания новостей.'
                                        f'Детали ошибки: {error}.'},
                            status=status.HTTP_400_BAD_REQUEST, )