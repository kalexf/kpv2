# Generated by Django 4.0.2 on 2022-05-11 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0033_profile_wtd_distance'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='customname',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]