# Generated by Django 4.0.2 on 2022-03-26 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0018_alter_profile_start_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='schedule_length',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
