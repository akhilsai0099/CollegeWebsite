# Generated by Django 4.2.2 on 2023-08-05 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminControl', '0006_alter_userdata_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='minorsmodel',
            name='courseChoice3',
            field=models.CharField(default=None, max_length=5, null=True),
        ),
    ]