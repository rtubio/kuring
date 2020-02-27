# Generated by Django 3.0.3 on 2020-02-27 09:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasker', '0004_task_result'),
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp marking when the event occurred, autofilled by model creation')),
                ('event', models.CharField(choices=[('N', 'New'), ('R', 'Running'), ('P', 'Paused'), ('D', 'Finished')], default='N', editable=False, max_length=1, verbose_name='Execution status for this experiment, 1 character among the available options')),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.AddField(
            model_name='task',
            name='events',
            field=models.ManyToManyField(to='tasker.Events', verbose_name='List of events related with the execution lifecycle of this task'),
        ),
    ]