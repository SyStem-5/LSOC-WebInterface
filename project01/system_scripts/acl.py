# Disable annoying 'no member' error
# pylint: disable=E1101

from django.core.exceptions import ObjectDoesNotExist

from project01.models import LSOCProfile

from project01.websockets.commands import element_update_send

profiles = LSOCProfile.objects.all()

online_users = {}


class InvalidData(Exception):
    pass


async def authorize_element_set(user, data):
    try:
        permissions = profiles.get(user=user).lsoc_permissions

        nodeIdentifier = data["node_identifier"]
        elementIdentifier = data["element_identifier"]

    except ObjectDoesNotExist:
        print("Could not check ACL - this user does not have an LSOC profile entry. User:", user)

    except (TypeError, KeyError):
        raise InvalidData

    else:
        if permissions.get(nodeIdentifier) and elementIdentifier in permissions[nodeIdentifier]:
            return True

    return False


def distribute_element_update(nodeIdentifier, elementIdentifier, data):
    for user in online_users.items():
        try:
            permissions = profiles.get(user=user[1]).lsoc_permissions

        except ObjectDoesNotExist:
            print("Could not check ACL - this user does not have an LSOC profile entry. User:", user[1].username)

        else:
            if permissions.get(nodeIdentifier) and elementIdentifier in permissions[nodeIdentifier]:
                element_update_send(user[0], data)


def filter_node_list(user, data):
    try:
        permissions = profiles.get(user=user).lsoc_permissions

    except ObjectDoesNotExist:
        print("Could not check ACL - this user does not have an LSOC profile entry. User:", user)
        return []

    else:
        filteredList = []

        for node in data:
            nodeID = node["identifier"]
            if not nodeID in permissions:
                continue

            nodeT = node.copy()

            nodeT["elements"] = []

            for element in node["elements"]:
                if element["address"] in permissions[nodeID]:
                    nodeT["elements"].append(element)

            filteredList.append(nodeT)

        return filteredList
