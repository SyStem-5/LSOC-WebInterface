# Disable annoying 'no member' error
# pylint: disable=E1101
# Disable project01.models import false-positive
# pylint: disable=E0401

# Called from views.py
import json
from enum import Enum

from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.db import connection
from channels.layers import get_channel_layer
from project01.models import MQTTConfig
from project01.settings import DATABASES, DEBUG
import paho.mqtt.client as mqtt


main_topic = "external_interface"

ws_superuser_groups = ['node_state']
ws_normaluser_groups = ['blackbox_state']

class CommandType(Enum):
    NodeElementList = "NodeElementList"
    DiscoveryEnable = "DiscoveryEnable"
    DiscoveryDisable = "DiscoveryDisable"
    AddToUnregisteredList = "AddToUnregisteredList"
    AnnounceOnline = "AnnounceOnline"
    AnnounceOffline = "AnnounceOffline"
    NodeRegistration = "NodeRegistration"
    UnregisterNode = "UnregisterNode"
    NodeOnline = "NodeOnline"
    NodeOffline = "NodeOffline"
    UpdateNodeInfo = "UpdateNodeInfo"

class WSCommandType(Enum):
    NodeState = "NodeState"
    BlackBoxState = "BlackBoxState"

class WSType(Enum):
    NodeState = "node.state"
    BlackBoxState = "blackbox.state"

# def ws_command_creator(ws_type, command, data):
#     payload = {"type": ws_type.value, "command": command.name, "data": data}
#     return payload


print("MQTT: Initializing MQTT Client sub-system...")

node_element_list = None
unregistered_nodes_list = []
discovery_mode = False
blackbox_status = False

db_connected = True
mqtt_config_db_table_name = "project01_mqttconfig"

if mqtt_config_db_table_name not in connection.introspection.table_names():
    db_connected = False
    print("MQTTSettings database table does not exist. Skipping MQTT Init.")

if db_connected:
    # Fetch client config from database
    settings = MQTTConfig.objects.all()

    if len(settings) > 0:
        print("MQTT: Client Loaded\n")
        settings = settings[0]
    else:
        print("MQTT: No mqtt client configuration found.")
        print("MQTT: Creating and using a default configuration.\n")
        def_config = MQTTConfig()
        def_config.ip = '127.0.0.1'
        def_config.port = 8883
        def_config.username = 'external_interface'
        def_config.password = ''
        def_config.save()
        settings = def_config


    def blackbox_new_command(commandType, data="", send=False):
        command = '{"command" : "' + commandType.name + \
            '", "data" : "' + data + '"}'

        if not send:
            return command
        else:
            client.publish(topic=main_topic+"/"+settings.username, payload=command)


    def blackbox_discovery_enable():
        print("BlackBox: Enabling Discovery")

        # Remove the old list
        global unregistered_nodes_list
        unregistered_nodes_list = []

        global discovery_mode
        discovery_mode = True

        blackbox_new_command(CommandType.DiscoveryEnable, send=True)
        return JsonResponse({"data": "ok"})


    def blackbox_discovery_disable():
        print("BlackBox: Disabling Discovery")

        global discovery_mode
        discovery_mode = False

        blackbox_new_command(CommandType.DiscoveryDisable, send=True)
        return JsonResponse({"data": "ok"})


    def blackbox_node_registration(data):
        node = {}
        elements = []

        data.pop("csrfmiddlewaretoken")
        for key in data:
            if key == "node_identifier":
                node["unreged_id"] = data[key]
            elif key == "node_name":
                node[key] = data[key]
            elif key == "node_category":
                node[key] = data[key]
            elif not key.startswith('elemtype_'):
                elements.append({"node_id": "", "address": key, "name": data[key], "element_type": data['elemtype_'+key], "data": "0"})

        node["elements"] = elements

        blackbox_new_command(CommandType.NodeRegistration, data=json.dumps(node).replace('"', "'"), send=True)
        print("BlackBox: Registering a node. ID:", data["node_identifier"])

        # Since we have a new node, we need to update the Node/Element list
        blackbox_new_command(CommandType.NodeElementList, send=True)

        blackbox_discovery_disable()

        return JsonResponse({"data": "ok"})

    def blackbox_update_node_info(data):
        node = {}
        elements = []

        data.pop("csrfmiddlewaretoken")
        for key in data:
            if key == "node_identifier":
                node["identifier"] = data[key]
            elif key == "node_name":
                node["name"] = data[key]
            elif key == "node_category":
                node["category"] = data[key]
            else:
                elements.append({"address": key, "name": data[key]})

        node["elements"] = elements

        blackbox_new_command(CommandType.UpdateNodeInfo, data=json.dumps(node).replace('"', "'"), send=True)
        print("BlackBox: Sending edited node information. ID:", data["node_identifier"])

        # Since we have a new node, we need to update the Node/Element list
        blackbox_new_command(CommandType.NodeElementList, send=True)

        return JsonResponse({"data": "ok"})

    def blackbox_send_node_command(data):
        command = data["command"]
        data = data["data"]

        if len(command) > 20 or len(data) > 20 or len(command) < 2:
            return JsonResponse({"data": "rejected"})

        if command == "unregister":
            blackbox_new_command(CommandType.UnregisterNode, data, send=True)
        elif command == "restart":
            return JsonResponse({"data": "unimplemented"})

        blackbox_new_command(CommandType.NodeElementList, send=True)
        return JsonResponse({"data": "ok"})


    def set_node_state(node_identifier, node_state):
        global node_element_list
        for node in node_element_list:
            if node['identifier'] == node_identifier:
                node_element_list[node_element_list.index(node)]['state'] = node_state

        node_ide = str(node_identifier)
        node_sta = str(node_state).lower()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            ws_superuser_groups[0],
            {"type": WSType.NodeState.value, "command": WSCommandType.NodeState.name, "node_id": str(node_ide), "state": str(node_sta)}
            #ws_command_creator(WSType.NodeState, WSCommandType.NodeState, str(node_ide+','+node_sta))
        )


    def on_connect(client, userdata, flags, rc):
        print("MQTT: Connected with result code " + str(rc) + "\n")

        blackbox_new_command(CommandType.AnnounceOnline, send=True)

        client.subscribe(main_topic, qos=1)


    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("MQTT: Failed to connect to broker. rc =", rc)
        else:
            print("MQTT: Client Disconnect.")


    def on_message(client, userdata, msg):
        if msg.topic == "external_interface":
            global discovery_mode
            global blackbox_status

            command = str(msg.payload.decode("utf-8")).replace('\\', '', 0)

            try:
                cmd = json.loads(command).get("command")
                data = json.loads(command).get("data")
                print("MQTT: Command -", cmd)

                try:
                    data = json.loads(json.loads(command).get("data"))
                except:
                    pass

                if cmd == CommandType.NodeElementList.name:
                    global node_element_list
                    node_element_list = data

                elif cmd == CommandType.AddToUnregisteredList.name:
                    if data not in unregistered_nodes_list:
                        unregistered_nodes_list.append(data)

                elif cmd == CommandType.AnnounceOffline.name:
                    discovery_mode = False
                    blackbox_status = False
                    print("BlackBox is Offline.")

                elif cmd == CommandType.AnnounceOnline.name:
                    blackbox_status = True

                    blackbox_new_command(CommandType.NodeElementList, send=True)
                    print("BlackBox is Online.")

                elif cmd == CommandType.NodeOnline.name:
                    set_node_state(data, True)

                elif cmd == CommandType.NodeOffline.name:
                    set_node_state(data, False)

                else:
                    print("Unknown command received,", cmd)
            except Exception as e:
                print("MQTT Message:", e, " Message:", command)

            # print(msg.payload.decode("utf-8"))
        else:
            print("Message received on an unknown topic:", msg.topic)
            print("With Message:", msg.payload)


    def on_subscribe(client, userdata, mid, granted_qos):
        #print("MQTT: Subscribe successfull")
        blackbox_new_command(CommandType.NodeElementList, send=True)


    client = mqtt.Client(client_id=settings.username)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect


    def connect_mqtt():
        print("MQTT: Connecting to", settings.ip)
        try:
            client.username_pw_set(username=settings.username,
                                password=settings.password)
            client.will_set(topic=main_topic+"/"+settings.username,
                            payload=blackbox_new_command(CommandType.AnnounceOffline),
                            qos=1)
            #print("MQTT: Skipping connection...")

            if DEBUG:
                client.tls_set(ca_certs="/etc/mosquitto/ca.crt")
                # This is a temporary fix
                client.tls_insecure_set(True)
            else:
                print("CONNECTING WITH MQTT IS NOT POSSIBLE DUE TO CERTIFICATE NOT HAVING A SAN FIELD.")
                # This WILL FAIL in a production environment
                client.tls_set(ca_certs="/mosquitto/config/ca.crt")

            client.connect(host=settings.ip, port=settings.port, keepalive=30)
            #client.connect_async(host=settings.ip, port=settings.port, keepalive=30)
            client.loop_start()
        except Exception as e:
            print("MQTT:", e)


    connect_mqtt()


    def disconnect_mqtt():
        blackbox_new_command(CommandType.DiscoveryDisable, send=True)

        client.disconnect()
        client.loop_stop()


    def update_mqttconfig(config):
        new_config = MQTTConfig(id=1,
                                ip=config.cleaned_data['ip'],
                                port=config.cleaned_data['port'],
                                username=config.cleaned_data['username'],
                                password=config.cleaned_data['password'])
        new_config.save()

        # We just updated the settings, we should disconnect to broker so we can connect with new settings
        disconnect_mqtt()

        return new_config
