# Generated by Django 4.0.2 on 2022-04-01 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0022_alter_profile_schedule_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='schedule_init_date',
            field=models.DateField(null=True),
        ),
    ]