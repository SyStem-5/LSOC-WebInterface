# Disable annoying 'no member' error
# pylint: disable=E1101

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from project01.fields import IntegerRangeField


class LSOCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lsoc_permissions = JSONField(blank=True)
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username


class MQTTConfig(models.Model):
    ip = models.CharField(max_length=500)
    port = IntegerRangeField(min_value=1, max_value=5)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=250)


class Zones(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
