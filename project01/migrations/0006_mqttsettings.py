# Generated by Django 2.1.3 on 2018-11-17 17:25

from django.db import migrations, models
import project01.fields


class Migration(migrations.Migration):

    dependencies = [
        ('project01', '0005_lsocprofile_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='MQTTSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('port', project01.fields.IntegerRangeField()),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
    ]
