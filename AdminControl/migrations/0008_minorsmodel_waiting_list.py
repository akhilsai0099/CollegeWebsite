# Generated by Django 4.2.2 on 2023-08-13 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminControl', '0007_minorsmodel_coursechoice3'),
    ]

    operations = [
        migrations.AddField(
            model_name='minorsmodel',
            name='waiting_list',
            field=models.CharField(default=None, max_length=5, null=True),
        ),
    ]
