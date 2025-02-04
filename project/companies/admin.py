from django.contrib import admin
from .models import Company, Structure, StructureMember

admin.site.register(Company)
admin.site.register(Structure)
admin.site.register(StructureMember)
