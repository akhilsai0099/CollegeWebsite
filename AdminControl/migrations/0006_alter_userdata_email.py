# Generated by Django 4.2.2 on 2023-07-07 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminControl', '0005_alter_minorsmodel_selecteddept'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]