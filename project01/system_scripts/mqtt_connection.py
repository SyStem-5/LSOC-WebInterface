# Disable annoying 'no member' error
# pylint: disable=E1101

from time import sleep
# Initialized from consumers.py
import json

import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import connection

import project01.system_scripts.lsoc as lsoc
from project01.models import MQTTConfig
from project01.settings import DEBUG
from project01.websockets.commands import WSLSOC
from project01.websockets.groups import (node_control_panel, node_register,
                                         system_info)

mqtt_debug_string = ">>MQTT:"

settings = None
client = None
is_connected = False


def init_mqtt():
    global settings, client

    mqtt_config_db_table_name = "project01_mqttconfig"
    if mqtt_config_db_table_name in connection.introspection.table_names():

        print("\n" + mqtt_debug_string, "Initializing...")

        # Fetch client config from database
        settings = MQTTConfig.objects.all()

        if len(settings) > 0:
            print(mqtt_debug_string, "Configuration Loaded\n")
            settings = settings[0]
        else:
            print(mqtt_debug_string, "No mqtt client configuration found.")
            print(mqtt_debug_string, "Creating and using a default configuration.\n")
            def_config = MQTTConfig()
            def_config.ip = 'mosquitto'
            def_config.port = 8883
            def_config.username = 'external_interface'
            def_config.password = ''
            def_config.save()
            settings = def_config

    client = mqtt.Client(client_id=settings.username)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    print(mqtt_debug_string, "Connecting to", settings.ip)

    client.username_pw_set(username=settings.username,
                            password=settings.password)

    client.will_set(topic=f"{lsoc.mqtt_main_topic}/{settings.username}",
                    payload=lsoc.newCommand(
                        None, lsoc.CommandType.AnnounceOffline),
                    qos=1)

    if DEBUG:
        client.tls_set(ca_certs="/etc/mosquitto/ca.crt")
    else:
        client.tls_set(ca_certs="/run/secrets/mqtt_ca.crt")

    while True:
        try:
            client.connect(host=settings.ip, port=settings.port, keepalive=30)
            # client.connect_async(host=settings.ip, port=settings.port, keepalive=30)
            client.loop_start()

            break
        except Exception as e:
            print("{} {} \n".format(mqtt_debug_string, e))

        sleep(2)


def on_connect(client, userdata, flags, rc):
    global is_connected
    is_connected = True
    ws_mqtt_state(TX=True)

    print(mqtt_debug_string, "Connected with result code {} \n".format(str(rc)))

    lsoc.newCommand(client, lsoc.CommandType.AnnounceOnline)

    client.subscribe(lsoc.mqtt_main_topic, qos=1)


def on_disconnect(client, userdata, rc):
    global is_connected
    is_connected = False
    ws_mqtt_state(TX=True)

    if rc != 0:
        print(mqtt_debug_string, "Failed to connect to broker. rc =", rc)
    else:
        print(mqtt_debug_string, "Client Disconnect.")

    lsoc.set_blackbox_state(False)
    ws_blackbox_state(TX=True)


def on_message(client, userdata, msg):
    if msg.topic == lsoc.mqtt_main_topic:

        command = str(msg.payload.decode("utf-8")).replace('\\', '', 0)

        try:
            cmd = json.loads(command).get("command")

            data = json.loads(command).get("data")
            # print(mqtt_debug_string, "Command -", cmd)

            try:
                data = json.loads(
                    json.loads(command).get("data")
                )
            except:
                pass

            if cmd == lsoc.CommandType.NodeElementList.name:
                lsoc.registeredNodes = data

            elif cmd == lsoc.CommandType.UpdateElementState.name:
                lsoc.update_element_state(data)

            elif cmd == lsoc.CommandType.AddToUnregisteredList.name:
                if data not in lsoc.unregistered_nodes:
                    lsoc.unregistered_nodes.append(data)
                    ws_command_send(node_register['unreged_new'], WSLSOC.UnregedListNew, json.dumps(data))
            elif cmd == lsoc.CommandType.RemoveFromUnregisteredList.name:
                for node in lsoc.unregistered_nodes:
                    if node["identifier"] == data:
                        lsoc.unregistered_nodes.remove(node)
                        # Only if we actually remove a node from the unreged list, notify the clients
                        ws_command_send(node_register['unreged_offline'], WSLSOC.UnregedListOffline, data)
            elif cmd == lsoc.CommandType.NodeRegistration.name:
                reged_node = data

                # TODO: When we get this, add this node to the registered node list
                # TODO: The data we get is not good for that, so BB should be adapted to return that data

                # Remove the registered node from the unregistered list
                for node in lsoc.unregistered_nodes:
                    if node["identifier"] == reged_node["identifier"]:
                        lsoc.unregistered_nodes.remove(node)

                # Send a notification to the clients
                ws_command_send(node_register['new_registered'], WSLSOC.NodeRegisteredNew, reged_node["identifier"])

            elif cmd == lsoc.CommandType.AnnounceOffline.name:
                lsoc.set_blackbox_state(False)
                ws_blackbox_state(TX=True)
            elif cmd == lsoc.CommandType.AnnounceOnline.name:
                lsoc.set_blackbox_state(True)
                ws_blackbox_state(TX=True)
                lsoc.newCommand(client, lsoc.CommandType.NodeElementList)

            elif cmd == lsoc.CommandType.ComponentStates.name:
                send_ws_neco_state(data)
            elif cmd == lsoc.CommandType.ComponentLog.name:
                ws_command_send(system_info['component_state'], WSLSOC.ComponentLog, data)
            elif cmd == lsoc.CommandType.State.name:
                ws_command_send(system_info['update_state'], WSLSOC.UpdateState, data)
            elif cmd == lsoc.CommandType.Changelogs.name:
                ws_command_send(system_info['changelogs'], WSLSOC.UpdateChangelog, data)
            elif cmd == lsoc.CommandType.UpdateStarted.name:
                ws_command_send(system_info['update_state'], WSLSOC.UpdateStart, "")

            elif cmd == lsoc.CommandType.NodeStatus.name:
                dataParsed = str(data).split('::', 1)
                ws_command_send(node_control_panel['node_state_update'], WSLSOC.NodeState, json.dumps(lsoc.setNodeState(dataParsed[0], dataParsed[1])))

            else:
                print("Unknown command received,", cmd)
        except Exception as e:
            print("[MQTT ERROR] Message:", e, " Message:", command)

        # print(msg.payload.decode("utf-8"))
    else:
        print("Message received on an unknown topic:", msg.topic)
        print("With Message:", msg.payload)


def on_subscribe(client, userdata, mid, granted_qos):
    lsoc.newCommand(client, lsoc.CommandType.NodeElementList)


def disconnect_mqtt():
    lsoc.newCommand(client, lsoc.CommandType.DiscoveryDisable)

    client.disconnect()
    client.loop_stop()


def update_mqttconfig(config):
    global settings

    new_config = MQTTConfig(id=1,
                            ip=config.cleaned_data['ip'],
                            port=config.cleaned_data['port'],
                            username=config.cleaned_data['username'],
                            password=config.cleaned_data['password'])
    new_config.save()

    # We just updated the settings, we should disconnect to broker so we can connect with new settings
    disconnect_mqtt()

    settings = new_config


def ws_command_creator(ws_type, data=""):
    return {"command": ws_type.name, "data": data}


def ws_command_send(group, ws_type, data):
    cmd = {"type": ws_type.value, "command": ws_type.name, "data": data}
    async_to_sync(get_channel_layer().group_send)(group, cmd)


def ws_mqtt_state(TX=False):
    response = {"component": "mqtt", "state": is_connected}
    if TX:
        ws_command_send(system_info['component_state'], WSLSOC.SystemStatus, response)
    else:
        return ws_command_creator(WSLSOC.SystemStatus, response)


def ws_blackbox_state(TX=False):
    response = {"component": "blackbox", "state": lsoc.get_blackbox_state()}
    if TX:
        ws_command_send(system_info['component_state'], WSLSOC.SystemStatus, response)
    else:
        return ws_command_creator(WSLSOC.SystemStatus, response)


def send_ws_neco_state(data):
    response = {"component": "neco", "data": data}
    ws_command_send(system_info['component_state'], WSLSOC.SystemStatus, response)
