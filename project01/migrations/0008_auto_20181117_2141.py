# Generated by Django 2.1.3 on 2018-11-17 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project01', '0007_auto_20181117_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mqttconfig',
            name='password',
            field=models.CharField(max_length=250),
        ),
    ]
