# Disable annoying 'no member' error
# pylint: disable=E1101

from django.core.exceptions import ObjectDoesNotExist

from project01.models import Zones


def return_message(state, data=""):
    return {"data": {"state": state, "data": data}}


def get_zones():
    return {"data": list(Zones.objects.all().values())}


def add_zone(data):
    try:
        if data["zone_name"]:
            Zones(name=data["zone_name"]).save()
        else:
            raise KeyError
    except (KeyError, TypeError):
        return return_message(False, "Could not parse received data.")

    return return_message(True, data["zone_name"])


def remove_zone(data):
    try:
        zoneID = int(data)

        zone = Zones.objects.get(id=zoneID)
        zone.delete()
    except ValueError:
        return return_message(False, "Could not parse received data.")
    except ObjectDoesNotExist:
        return return_message(False, "Zone does not exist.")

    return return_message(True, zone.name)


def edit_zone(data):

    try:
        zoneID = int(data["zone_id"])
        zoneName = str(data["zone_name"])

        zone = Zones.objects.get(id=zoneID)
        zone.name = zoneName

        zone.save()
    except ValueError:
        return return_message(False, "Could not parse received data.")
    except ObjectDoesNotExist:
        return return_message(False, "Zone does not exist.")

    return return_message(True, zone.name)
