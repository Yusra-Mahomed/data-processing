# Generated by Django 3.2.25 on 2024-04-01 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='processed_data',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='processed_file_pkl',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
