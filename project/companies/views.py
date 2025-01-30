from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from companies.models import Company, Structure
from companies.serializers import CompanySerializer, StructureSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с Компаниями.
    """

    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class StructureViewSet(viewsets.ModelViewSet):
    """
    Класс для операций с Организационными структурами.
    """

    serializer_class = StructureSerializer
    queryset = Structure.objects.all()
