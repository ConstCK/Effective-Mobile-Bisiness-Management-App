from rest_framework import serializers

from companies.models import Company, Structure, StructureMember


class StructureSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['id', 'name']
        model = Structure


class StructureMemberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    structure = serializers.CharField(source='structure.name', read_only=True)

    class Meta:
        fields = ['id', 'structure', 'position', 'role', 'subordinates', 'bosses']
        model = StructureMember


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    structure_detail = serializers.CharField(source='structure', read_only=True)

    class Meta:
        fields = ['id', 'name', 'structure', 'structure_detail']
        model = Company
        extra_kwargs = {
            'structure': {'write_only': True},
        }
