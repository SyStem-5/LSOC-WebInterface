# Generated by Django 2.1.3 on 2018-11-10 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project01', '0002_auto_20181110_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lsocpermission',
            name='permission',
            field=models.TextField(default='*'),
        ),
    ]
