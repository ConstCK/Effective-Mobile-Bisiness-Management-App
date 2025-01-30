from django.db import models


class Structure(models.Model):
    name = models.CharField(max_length=128, unique=True,
                            verbose_name='Название организационной структуры')

    def __str__(self) -> str:
        return f'Организационная структура - {self.name}'

    class Meta:
        verbose_name = 'Организационная структура'
        verbose_name_plural = 'Организационные структуры'


class StructureMember(models.Model):
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE,
                                  related_name='members',
                                  verbose_name='Название организационной структуры')
    position = models.CharField(max_length=64,
                                verbose_name='Позиция в команде')
    role = models.CharField(max_length=64, verbose_name='Роль в команде')
    subordinates = models.CharField(max_length=64, null=True,
                                    verbose_name='Непосредственные начальники')
    bosses = models.CharField(max_length=64, null=True,
                              verbose_name='Непосредственные подчиненные')

    def __str__(self) -> str:
        return f'Член структуры - {self.position}'

    class Meta:
        verbose_name = 'Член организационной структуры'
        verbose_name_plural = 'Члены организационной структуры'


class Company(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='Название компании')
    structure = models.ForeignKey(Structure, on_delete=models.PROTECT,
                                  related_name='companies',
                                  verbose_name='Организационная структура')

    def __str__(self) -> str:
        return f'Команда {self.name}'

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
