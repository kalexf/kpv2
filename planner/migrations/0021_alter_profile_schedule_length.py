# Generated by Django 4.0.2 on 2022-03-28 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0020_remove_activity_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='schedule_length',
            field=models.PositiveSmallIntegerField(choices=[(1, '1 Week'), (2, '2 Weeks'), (4, '4 Weeks')], default=1),
        ),
    ]
