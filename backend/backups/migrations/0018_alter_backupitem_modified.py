# Generated by Django 3.2 on 2021-05-02 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0017_backupitem_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupitem',
            name='modified',
            field=models.TimeField(null=True),
        ),
    ]
