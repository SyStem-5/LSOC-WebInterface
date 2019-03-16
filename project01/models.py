# Disable annoying 'no member' error
# pylint: disable=E1101

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from project01.fields import IntegerRangeField


class LSOCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lsoc_permissions = models.TextField(default='*')
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        _lsoc_profile = LSOCProfile(
            user=kwargs['instance'],
            lsoc_permissions=kwargs['instance'].lsocprofile.lsoc_permissions,
            description=kwargs['instance'].lsocprofile.description)

        _lsoc_profile.save()


post_save.connect(create_profile, sender=User)


class MQTTConfig(models.Model):
    #ip = models.GenericIPAddressField()
    ip = models.CharField(max_length=500)
    port = IntegerRangeField(min_value=1, max_value=5)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=250)
    # Add additional fields for certs
