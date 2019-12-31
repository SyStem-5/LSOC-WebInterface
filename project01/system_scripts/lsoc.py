# Disable annoying 'no member' error
# pylint: disable=E1101

import json
from enum import Enum

from django.http import JsonResponse

from project01.models import Zones
#from project01.system_scripts.mqtt_connection import mqtt_main_topic
from project01.system_scripts.acl import distribute_element_update


class CommandType(Enum):
    # BlackBox
    NodeElementList = 1
    DiscoveryEnable = 2
    DiscoveryDisable = 3
    AddToUnregisteredList = 4
    RemoveFromUnregisteredList = 5
    AnnounceOnline = 6
    AnnounceOffline = 7
    NodeRegistration = 8
    UnregisterNode = 9
    RestartNode = 10
    NodeStatus = 11
    UpdateNodeInfo = 12
    SetElementState = 13
    UpdateElementState = 14

    # NECO
    ComponentStates = 15
    ComponentLog = 16
    State = 17
    Changelogs = 18
    RefreshUpdateManifest = 19            # Alias for 'UpdateCheck'
    StartUpdateDownloadAndInstall = 20    # Alias for 'UpdateStart'
    UpdateStarted = 21
    SystemShutdown = 22
    SystemReboot = 23


unregistered_nodes = []
registeredNodes = []

discovery_mode = False
blackbox_status = False

mqtt_main_topic = "external_interface"


def return_msg(status=True, data=""):
    return {"status": status, "data": data}


def get_blackbox_state():
    return blackbox_status


def set_blackbox_state(state):
    global blackbox_status
    blackbox_status = state

    if state:
        print("BlackBox is Online.")
    else:
        print("BlackBox is Offline.")

    return blackbox_status


def getRegisteredNodes():
    return registeredNodes


def getUnregisteredNodes():
    return unregistered_nodes


def newCommand(client, commandType, data=""):
    command = '{{"command" : "{}", "data" : "{}"}}'.format(commandType.name, data)

    if not client:
        return command
    else:
        try:
            if not client.is_connected():
                raise Exception("Disconnected - cannot send payload.")

            client.publish(topic=mqtt_main_topic+"/" +
                           client._username.decode("utf-8"), payload=command)
        except Exception as e:
            print(e)
            return return_msg(False, f"MQTT -> Failed to send command ({commandType}): {e}")

        return return_msg(True)


def nodeDiscoveryEnable(client):
    if blackbox_status is False:
        return return_msg(False, "BlackBox is offline.")

    print("LSOC: Enabling Discovery")

    global unregistered_nodes
    unregistered_nodes = []

    return newCommand(client, CommandType.DiscoveryEnable)


def nodeDiscoveryDisable(client):
    if blackbox_status is False:
        return return_msg(False, "BlackBox is offline.")

    print("LSOC: Disabling Discovery")

    global unregistered_nodes
    unregistered_nodes = []

    return newCommand(client, CommandType.DiscoveryDisable)


def nodeRegistration(client, data):
    if blackbox_status is False:
        return return_msg(False, "BlackBox is offline.")

    print("LSOC: Registering a node. NodeID:", data["node_identifier"])

    node = {}
    elements = []

    try:
        for key in data:
            if key == "node_identifier":
                node["identifier"] = data[key]
            elif key == "node_name":
                node["name"] = data[key]

            elif str(key).endswith(':zone'):
                zoneID = int(data[key])
                if zoneID != -1 and not Zones.objects.filter(id=zoneID).exists():
                    raise ValueError

            elif ":" not in key:
                elements.append({
                    "address": key,
                    "name": data[key],
                    "element_type": data[key+":type"],
                    "zone": data[key+":zone"]
                })

        node["elements"] = elements
    except KeyError as e:
        print("LSOC ERROR -> {NodeRegistration}:", e)
        return return_msg(False, "Could not parse the node registration form data.")

    except ValueError:
        return return_msg(False, "Zone with that ID does not exist.")

    # TODO: Remove the last 5 lines and replace it with the one below,
    # so we don't ask for a new list for just one new node

    # return newCommand(client, CommandType.NodeRegistration, json.dumps(node).replace('"', '\\"'))
    response = newCommand(client, CommandType.NodeRegistration, json.dumps(node).replace('"', '\\"'))
    if not response["status"]:
        return response

    # Since we have a new node, we need to tell LSOC to send the new Node/Element list
    return newCommand(client, CommandType.NodeElementList)


def updateNodeInfo(client, data):
    if blackbox_status is False:
        return return_msg(False, "BlackBox is offline.")

    node = {}
    elements = []

    try:
        for key in data:
            if key == "node_identifier":
                node["identifier"] = data[key]
            elif key == "node_name":
                node["name"] = data[key]

            elif str(key).endswith(':zone'):
                zoneID = int(data[key])
                if zoneID != -1 and not Zones.objects.filter(id=zoneID).exists():
                    raise ValueError

            elif ":" not in key:
                elements.append({
                    "address": key,
                    "name": data[key],
                    "zone": data[key+":zone"]
                })

    except KeyError as e:
        print("LSOC ERROR -> {NodeEdit}:", e)
        return return_msg(False, "Could not parse the node data edit form data.")

    except ValueError:
        return return_msg(False, "Zone with that ID does not exist.")

    node["elements"] = elements

    response = newCommand(client, CommandType.UpdateNodeInfo, data=json.dumps(node).replace('"', '\\"'))
    if not response["status"]:
        return response

    print("LSOC: Sending edited node information. NodeID:", node["identifier"])

    # # Since we edited node data, we need to update the Node/Element list
    return newCommand(client, CommandType.NodeElementList)


def sendNodeCommand(client, data):
    if blackbox_status is False:
        return return_msg(False, "BlackBox is offline.")

    try:
        command = data["command"]
        identifier = data["data"]
    except Exception as e:
        print("LSOC ERROR -> {NodeCommand}:", e)
        return return_msg(False, "Could not parse the node command request data.")

    if command == "unregister":
        response = newCommand(client, CommandType.UnregisterNode, identifier)
        if not response["status"]:
            return response

    elif command == "restart":
        response = newCommand(client, CommandType.RestartNode, identifier)
        if not response["status"]:
            return response

    response = newCommand(client, CommandType.NodeElementList)
    if not response["status"]:
        return response

    return return_msg(True, "{}:{}".format(command, identifier))


def setNodeState(node_identifier, node_state):
    node_state = (node_state == "true")

    for node in registeredNodes:
        if node['identifier'] == node_identifier:
            node['state'] = node_state
            break

    return return_msg(node_state, node_identifier)


def update_element_state(data):
    dataS = str(data).split('::', 2)

    node_identifier = dataS[0]
    element_identifier = dataS[1]
    element_data = dataS[2]

    for node in registeredNodes:
        if node["identifier"] == node_identifier:
            for element in node["elements"]:
                if element["address"] == element_identifier:
                    element["data"] = element_data
                    distribute_element_update(node_identifier, element_identifier, data)
                    return


def set_element_state(mqtt_client, data):
    try:
        validate_element_set_data(data["element_type"], data["data"])

        data["data"] = data["data"].replace('"', "'")
    except (KeyError, TypeError, ValueError):
        return return_msg(False, "Invalid ElementSet data.")

    # from project01.system_scripts.mqtt_connection import client as mqtt_client
    return newCommand(mqtt_client, CommandType.SetElementState, json.dumps(data).replace('"', '\\"'))


def validate_element_set_data(elem_type, data):
    if elem_type == "BasicSwitch":
        if not isinstance(data, str):
            raise ValueError
        if data != "true" and data != "false":
            raise ValueError
    elif elem_type == "Thermostat":
        if not isinstance(data, str):
            raise ValueError
        if data != "+" and data != "-":
            raise ValueError
    elif elem_type == "DHT11":
        print("Cannot set a read-only element. <DHT11>")
        raise ValueError
    else:
        print("Cannot validate unknown element.")
        raise ValueError

def system_shutdown_reboot(mqtt_client, action: str):
    if "reboot" in action:
        print("{LSOC} system_shutdown_reboot() -> Sending reboot command...")

        msg = newCommand(mqtt_client, CommandType.SystemReboot)
        return {"command": "SystemReboot", "status": msg["status"], "data": msg["data"]}
    elif "shutdown" in action:
        print("{LSOC} system_shutdown_reboot() -> Sending shutdown command...")

        msg = newCommand(mqtt_client, CommandType.SystemShutdown)
        return {"command": "SystemShutdown", "status": msg["status"], "data": msg["data"]}


class NeutronCommunicator():

    @staticmethod
    async def requestComponentLog(client, data):
        payload = {'request': data['request'], 'component': data['component']}
        cmd = newCommand(None, CommandType.ComponentLog, json.dumps(payload).replace('"', "'"))

        # We publish this to the NECO id instead of the NECO root topic
        client.publish(topic=f"neutron_communicators/{data['id']}", payload=cmd, qos=1)


    @staticmethod
    async def requestStates(client):
        cmd = newCommand(None, CommandType.ComponentStates)
        client.publish(topic="neutron_communicators", payload=cmd, qos=1)


    @staticmethod
    async def requestUpdateCheck(client):
        cmd = newCommand(None, CommandType.RefreshUpdateManifest)
        client.publish(topic="neutron_communicators", payload=cmd, qos=1)


    @staticmethod
    async def requestUpdateStart(client):
        cmd = newCommand(None, CommandType.StartUpdateDownloadAndInstall)
        client.publish(topic="neutron_communicators", payload=cmd, qos=1)
