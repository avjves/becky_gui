# Generated by Django 3.2 on 2021-04-29 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0009_auto_20210429_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupstatus',
            name='running',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
