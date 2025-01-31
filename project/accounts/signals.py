from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import Profile


# Сигнал на создание Профиля пользователя с дополнительными полями при регистрации User
# @receiver(post_save, sender=User)
# def initial_task(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance, is_administrator=instance.is_staff)
