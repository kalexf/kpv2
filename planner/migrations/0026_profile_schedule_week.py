# Generated by Django 4.0.2 on 2022-04-11 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0025_rename_schedule_profile_plan_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='schedule_week',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]