# Generated by Django 4.0.2 on 2022-02-09 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0008_alter_pacedrun_pace'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='my_type',
            field=models.CharField(default='', max_length=20),
        ),
    ]
