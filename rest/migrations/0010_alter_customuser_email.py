# Generated by Django 5.1.5 on 2025-02-02 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0009_rename_refresh_expire_time_customuser_refresh_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=32, unique=True),
        ),
    ]
