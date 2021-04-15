# Generated by Django 3.2 on 2021-04-15 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0003_remove_backup_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('path', models.TextField()),
                ('backup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='backups.backup')),
            ],
        ),
    ]
