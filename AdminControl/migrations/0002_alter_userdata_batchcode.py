# Generated by Django 4.2.4 on 2023-08-27 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminControl', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='batchCode',
            field=models.CharField(max_length=9),
        ),
    ]
