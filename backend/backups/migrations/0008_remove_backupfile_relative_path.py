# Generated by Django 3.2 on 2021-04-27 22:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0007_backup_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backupfile',
            name='relative_path',
        ),
    ]
