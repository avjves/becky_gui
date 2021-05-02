# Generated by Django 3.2 on 2021-05-02 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0015_auto_20210501_2332'),
    ]

    operations = [
        migrations.CreateModel(
            name='DifferentialInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.TextField()),
                ('modified', models.TimeField()),
                ('diff_creation', models.TimeField(auto_now=True)),
                ('order', models.IntegerField()),
                ('backup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backups.backup')),
            ],
        ),
    ]