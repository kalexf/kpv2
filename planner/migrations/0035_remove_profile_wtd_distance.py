# Generated by Django 4.0.2 on 2022-05-28 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0034_activity_customname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='wtd_distance',
        ),
    ]
