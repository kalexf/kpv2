# Generated by Django 4.0.2 on 2022-05-01 20:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0030_profile_current_week_initial_profile_history_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='last_exercise',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='mileage',
        ),
    ]