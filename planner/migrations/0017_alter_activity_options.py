# Generated by Django 4.0.2 on 2022-02-21 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0016_profile_mileage_profile_mileage_increment_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['last_done']},
        ),
    ]
