# Generated by Django 3.2 on 2021-04-11 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupparameter',
            name='backup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='backups.backup'),
        ),
    ]
