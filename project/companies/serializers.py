from rest_framework import serializers

from companies.models import Company, Structure


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name', 'structure']
        model = Company


class StructureSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name']
        model = Structure


class StructureMemberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'structure', 'position', 'role', 'subordinates', 'bosses']
        model = Structure
