# Disable annoying 'no member' error
# pylint: disable=E1101

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from project01.fields import IntegerRangeField


class LSOCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lsoc_permissions = models.TextField(default='*')
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # This will create a default instance if it wasn't provided, if it was provided it will insert it
    try:
        lsoc_profile = LSOCProfile(
            user=instance,
            lsoc_permissions=instance.lsocprofile.lsoc_permissions,
            description=instance.lsocprofile.description)

        lsoc_profile.save()
    except ObjectDoesNotExist:
        LSOCProfile.objects.get_or_create(user=instance)


class MQTTConfig(models.Model):
    #ip = models.GenericIPAddressField()
    ip = models.CharField(max_length=500)
    port = IntegerRangeField(min_value=1, max_value=5)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=250)
    # Add additional fields for certs
