# Generated by Django 3.2 on 2021-05-11 23:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0021_backupitem_file_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='differentialinformation',
            name='diff_creation',
        ),
        migrations.RemoveField(
            model_name='differentialinformation',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='differentialinformation',
            name='order',
        ),
        migrations.AddField(
            model_name='backupitem',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 11, 23, 49, 16, 417991, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='differentialinformation',
            name='current_modified',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='differentialinformation',
            name='previous_modified',
            field=models.DateTimeField(null=True),
        ),
    ]