# Generated by Django 3.2 on 2021-05-02 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0019_alter_differentialinformation_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupitem',
            name='checksum',
            field=models.CharField(default=0, max_length=64),
            preserve_default=False,
        ),
    ]
