# Generated by Django 4.0.2 on 2022-05-02 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0032_remove_profile_mileage_increment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wtd_distance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
