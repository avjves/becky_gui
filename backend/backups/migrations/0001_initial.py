# Generated by Django 3.2 on 2021-04-11 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('provider', models.CharField(max_length=128)),
                ('path', models.CharField(max_length=512)),
                ('running', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BackupParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=1024)),
                ('backup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backups.backup')),
            ],
        ),
    ]
