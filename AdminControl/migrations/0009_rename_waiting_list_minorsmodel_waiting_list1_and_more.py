# Generated by Django 4.2.2 on 2023-08-13 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminControl', '0008_minorsmodel_waiting_list'),
    ]

    operations = [
        migrations.RenameField(
            model_name='minorsmodel',
            old_name='waiting_list',
            new_name='waiting_list1',
        ),
        migrations.AddField(
            model_name='minorsmodel',
            name='waiting_list2',
            field=models.CharField(default=None, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='minorsmodel',
            name='waiting_list3',
            field=models.CharField(default=None, max_length=5, null=True),
        ),
    ]