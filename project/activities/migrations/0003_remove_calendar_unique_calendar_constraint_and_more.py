# Generated by Django 5.1.5 on 2025-02-01 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_profile_position'),
        ('activities', '0002_alter_calendar_name'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='calendar',
            name='Unique calendar constraint',
        ),
        migrations.AddConstraint(
            model_name='calendar',
            constraint=models.UniqueConstraint(fields=('name', 'owner', 'start_at', 'end_at'), name='Unique calendar constraint'),
        ),
    ]
