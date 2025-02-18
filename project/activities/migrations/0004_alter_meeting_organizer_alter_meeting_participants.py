# Generated by Django 5.1.5 on 2025-02-01 11:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_profile_position'),
        ('activities', '0003_remove_calendar_unique_calendar_constraint_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_meetings', to='accounts.profile', verbose_name='Организатор встречи'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='participants',
            field=models.ManyToManyField(related_name='participated_meetings', to='accounts.profile', verbose_name='Участники встречи'),
        ),
    ]
