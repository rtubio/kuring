# Generated by Django 3.0.3 on 2020-02-11 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasker', '0003_auto_20200209_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='result',
            field=models.TextField(default='', verbose_name='Task result, serialized JSON object'),
        ),
    ]
