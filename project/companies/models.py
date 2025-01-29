from django.db import models


class Structure(models.Model):
    name = models.CharField(max_length=128, unique=True,
                            verbose_name='Название организационной структуры')

    class Meta:
        verbose_name = 'Организационная структура'
        verbose_name_plural = 'Организационные структуры'


class StructureMember(models.Model):
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE,
                                  related_name='members',
                                  verbose_name='Название организационной структуры')
    position = models.CharField(min_length=64,
                                verbose_name='Позиция в команде')
    role = models.CharField(min_length=64, verbose_name='Роль в команде')
    subordinates = models.CharField(min_length=64, null=True,
                                    verbose_name='Непосредственные начальники')
    bosses = models.CharField(min_length=64, null=True,
                              verbose_name='Непосредственные подчиненные')

    class Meta:
        verbose_name = 'Член организационной структуры'
        verbose_name_plural = 'Члены организационной структуры'


class Company(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='Название компании')
    structure = models.ForeignKey(Structure, on_delete=models.SET_NULL,
                                  related_name='companies',
                                  verbose_name='Организационная структура')

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
