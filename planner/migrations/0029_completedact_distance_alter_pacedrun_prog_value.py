# Generated by Django 4.0.2 on 2022-04-17 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0028_completedact_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedact',
            name='distance',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='pacedrun',
            name='prog_value',
            field=models.CharField(choices=[('TIME', 'Time(minutes)'), ('DIST', 'Distance(km)')], default='TIME', max_length=4),
        ),
    ]
