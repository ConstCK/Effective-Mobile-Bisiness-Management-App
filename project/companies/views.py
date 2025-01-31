from http import HTTPMethod

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from companies.models import Company, Structure, StructureMember
from companies.serializers import CompanySerializer, StructureSerializer, StructureMemberSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с Компаниями.
    """

    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [IsAdminUser]

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        super().destroy(request, *args, **kwargs)
        return Response({'message': f'Успешное удаление объекта.'},
                        status=status.HTTP_200_OK, )


class StructureViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с Организационными структурами.
    """

    serializer_class = StructureSerializer
    queryset = Structure.objects.all()
    permission_classes = [IsAdminUser]

    # Добавление члена организационной структуры
    @action(methods=[HTTPMethod.POST, ], detail=True, url_path='add-member', )
    def add_member(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = StructureMemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = StructureMember(**serializer.validated_data)
            structure = Structure.objects.get(pk=kwargs.get('pk'))
            instance.structure = structure
            instance.save()
            return Response({'message': f'Успешное создание объекта.',
                             'data': serializer.data
                             },
                            status=status.HTTP_201_CREATED, )

        except Exception as error:
            return Response({'message': f'Ошибка добавления члена структуры.'
                                        f'Детали ошибки: {error}'},
                            status=status.HTTP_400_BAD_REQUEST, )

    # Удаление члена организационной структуры
    @action(methods=[HTTPMethod.DELETE, ], detail=True, url_path='delete-member', )
    def delete_member(self, request: Request, *args, **kwargs) -> Response:
        try:
            instance = StructureMember.objects.get(pk=kwargs.get('pk'))
            instance.delete()
            instance.save()
            return Response({'message': f'Успешное удаление объекта.'},
                            status=status.HTTP_200_OK, )

        except ObjectDoesNotExist:
            return Response({'message': 'Ошибка удаление члена структуры. Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
