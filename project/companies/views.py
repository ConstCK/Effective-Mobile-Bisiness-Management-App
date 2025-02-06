from http import HTTPMethod

from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from companies.models import Company, Structure, StructureMember
from companies.serializers import CompanySerializer, StructureSerializer, StructureMemberSerializer, \
    SuccessResponseWithMember
from accounts.serializers import Error400Response, SuccessResponse, Error404Response


@extend_schema(tags=['Company'])
class CompanyViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с Компаниями.
    """

    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [IsAdminUser]
    # Разрешенные методы класса
    http_method_names = ['head', 'options', 'get', 'post', 'delete', ]

    # Метод для удаления компании.
    @extend_schema(summary='Удаление компании',
                   responses={
                       status.HTTP_200_OK: OpenApiResponse(
                           response=SuccessResponse,
                           description='Успешное удаление компании'),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Ошибка удаления компании'),
                   },
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID компании',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        super().destroy(request, *args, **kwargs)
        return Response({'message': 'Успешное удаление компании.'},
                        status=status.HTTP_200_OK, )

    # Метод для получения компании.
    @extend_schema(summary='Получение компании',
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID компании',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Метод для получения списка компаний.
    @extend_schema(summary='Получение списка компаний', )
    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Метод для создания компании.
    @extend_schema(summary='Создание компании', )
    def create(self, request: Request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(tags=['Structure'])
class StructureViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с Организационными структурами.
    """

    serializer_class = StructureSerializer
    queryset = Structure.objects.all()
    permission_classes = [IsAdminUser]
    # Разрешенные методы класса
    http_method_names = ['head', 'options', 'get', 'post', 'delete', ]

    # Метод для удаления организационной структуры.
    @extend_schema(summary='Удаление организационной структуры',
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID структуры',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # Метод для добавления организационной структуры.
    @extend_schema(summary='Добавление организационной структуры', )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    # Метод для получения списка организационных структур.
    @extend_schema(summary='Получение списка организационных структур', )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Метод для получения указанной организационной структуры.
    @extend_schema(summary='Получение указанной организационной структуры',
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID структуры',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Добавление члена организационной структуры
    @extend_schema(summary='Добавление члена организационной структуры',
                   request=StructureMemberSerializer,
                   responses={
                       status.HTTP_201_CREATED: OpenApiResponse(
                           response=SuccessResponseWithMember,
                           description='Успешное добавление члена структуры'),
                       status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                           response=Error400Response,
                           description='Ошибка добавление члена структуры'),
                   },
                   examples=[
                       OpenApiExample(
                           'New member example',
                           description="Пример добавления члена организационной структуры",
                           value={
                               'position': 'Инженер',
                               'role': 'Контроль инвентаризации объектов',
                               'subordinates': 'Техники',
                               'bosses': 'Главный инженер'
                           },
                       )
                   ],
                   # Переопределение стандартного описания вводимого параметра пути
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID структуры',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    @action(methods=[HTTPMethod.POST, ], detail=True, url_path='add-member', )
    def add_member(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = StructureMemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = StructureMember(**serializer.validated_data)
            structure = Structure.objects.get(pk=kwargs.get('pk'))
            instance.structure = structure
            instance.save()

            return Response({'message': 'Успешное создание объекта.',
                             'data': serializer.data
                             },
                            status=status.HTTP_201_CREATED, )

        except Exception as error:
            return Response({'message': f'Ошибка добавления члена структуры.'
                                        f'Детали ошибки: {error}'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление члена организационной структуры
    @extend_schema(summary='Удаление члена организационной структуры',
                   responses={
                       status.HTTP_200_OK: OpenApiResponse(
                           response=SuccessResponse,
                           description='Успешное удаление члена структуры'),
                       status.HTTP_404_NOT_FOUND: OpenApiResponse(
                           response=Error404Response,
                           description='Ошибка удаления члена структуры'),
                   },
                   # Переопределение стандартного описания вводимого параметра пути
                   parameters=[
                       OpenApiParameter(
                           name='id',
                           location=OpenApiParameter.PATH,
                           description='Параметр для указания ID члена структуры',
                           required=True,
                           type=int
                       ),
                   ],
                   )
    @action(methods=[HTTPMethod.DELETE, ], detail=True, url_path='delete-member', )
    def delete_member(self, request: Request, *args, **kwargs) -> Response:
        try:
            instance = StructureMember.objects.get(pk=kwargs.get('pk'))
            instance.delete()

            return Response({'message': 'Успешное удаление объекта.'},
                            status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': 'Ошибка удаление члена структуры. Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
