import json
import threading
##TEMPORARY##
import urllib.request

from channels.generic.websocket import AsyncWebsocketConsumer

import project01.system_scripts.acl as ACL
import project01.system_scripts.mqtt_connection as MQTT
import project01.websockets.commands as WSCMD
from project01.system_scripts.account_management import (register_account,
                                                         staff_edit_account,
                                                         staff_remove_account)
from project01.system_scripts.mqtt_connection import (ws_blackbox_state,
                                                      ws_mqtt_state)
from project01.system_scripts.zones import (add_zone, edit_zone, get_zones,
                                            remove_zone)
from project01.websockets.groups import (node_control_panel, node_register,
                                         system_info, user)


# Async MQTT connection retries (executed only if we can't connect on django start)
mq = threading.Thread(target=MQTT.init_mqtt)
mq.start()

class Dashboard(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
            print("WS {{User}} -> {user} connected.".format(user=str(self.scope["user"])))

            await self.send(
                json.dumps(
                    WSCMD.new(
                        WSCMD.WSLSOC.RegisteredListGet,
                        json.dumps(
                            ACL.filter_node_list(self.scope["user"], MQTT.lsoc.getRegisteredNodes())
                        )
                    )
                )
            )

            gr = "{}-{}".format(user["element_state"], self.scope["user"].username)
            ACL.online_users[gr] = self.scope["user"]
            await self.channel_layer.group_add(gr, self.channel_name)

    async def disconnect(self, close_code):
        gr = "{}-{}".format(user["element_state"], self.scope["user"].username)
        del ACL.online_users[gr]
        await self.channel_layer.group_discard(gr, self.channel_name)

        print("WS {{User}} -> {user} disconnected. Code: {code}".format(
            user=str(self.scope["user"]),
            code=close_code))

    async def receive(self, text_data):
        await UserCommandDecoder.decode(self, text_data)

    async def element_state(self, event):
        '''Handles the "element.state" event before we send it out.'''
        await self.send(json.dumps(event))


class StaffAccountManagement(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_superuser:
            await self.accept()
            print("WS {{Staff}} <AM> -> {user} connected.".format(user=str(self.scope["user"])))

            await self.send(
                json.dumps(
                    WSCMD.new(WSCMD.WSLSOC.RegisteredListGet,
                    MQTT.lsoc.getRegisteredNodes())
                )
            )

    async def disconnect(self, close_code):
        print("WS {{Staff}} <AM> -> {user} disconnected. Code: {code}".format(
            user=str(self.scope["user"]),
            code=close_code))

    async def receive(self, text_data):
        await StaffCommandDecoder.decode(self, text_data)


class StaffNodeRegister(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_superuser:
            await self.accept()
            print("WS {{Staff}} <NR> -> {user} connected.".format(user=str(self.scope["user"])))
            for group in node_register:
                await self.channel_layer.group_add(node_register[group], self.channel_name)

            # Send the zones list after the user connects
            await self.send(
                json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.ZonesGet,
                        get_zones())
                )
            )

            # This is where turn on node discovery
            await self.send(
                json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.DiscoveryOn,
                        MQTT.lsoc.nodeDiscoveryEnable(MQTT.client)
                    )
                )
            )

    async def disconnect(self, close_code):
        for group in node_register:
            await self.channel_layer.group_discard(node_register[group], self.channel_name)
        print("WS {{Staff}} <NR> -> {user} disconnected. Code: {code}".format(
            user=str(self.scope["user"]),
            code=close_code))

        # This is where we turn off the node discovery
        await self.send(
                json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.DiscoveryOff,
                        MQTT.lsoc.nodeDiscoveryDisable(MQTT.client)
                    )
                )
            )

    async def receive(self, text_data):
        await StaffCommandDecoder.decode(self, text_data)

    async def unreged_list_new(self, event):
        '''Handles the "unreged_list.new" event before we send it out.'''
        await self.send(json.dumps(event))

    async def node_registered(self, event):
        '''Handles the "node.registered" event before we send it out.'''
        await self.send(json.dumps(event))

    async def unreged_list_offline(self, event):
        '''Handles the "unreged_list.offline" event before we send it out.'''
        await self.send(json.dumps(event))


class StaffNodeControlPanel(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_superuser:
            await self.accept()
            print("WS {{Staff}} <NCP> -> {user} connected.".format(user=str(self.scope["user"])))
            for group in node_control_panel:
                await self.channel_layer.group_add(node_control_panel[group], self.channel_name)

            # Send the zones list after the user connects
            await self.send(
                json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.ZonesGet,
                        get_zones())
                )
            )

            # Send the Node list when the user connects
            await self.send(
                json.dumps(
                    WSCMD.new(WSCMD.WSLSOC.RegisteredListGet,
                    MQTT.lsoc.getRegisteredNodes())
                )
            )

    async def disconnect(self, close_code):
        for group in node_control_panel:
            await self.channel_layer.group_discard(node_control_panel[group], self.channel_name)

        print("WS {{Staff}} <NCP> -> {user} disconnected. Code: {code}".format(
            user=str(self.scope["user"]),
            code=close_code))

    async def receive(self, text_data):
        await StaffCommandDecoder.decode(self, text_data)

    async def node_state(self, event):
        '''Handles the "node.state" event before we send it out.'''
        await self.send(json.dumps(event))


class StaffSystemStatus(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_superuser:
            await self.accept()
            print("WS {{Staff}} <SysStatus> -> {user} connected.".format(user=str(self.scope["user"])))
            for group in system_info:
                await self.channel_layer.group_add(system_info[group], self.channel_name)

            # Send a request to NECO for component states
            await MQTT.lsoc.NeutronCommunicator.requestStates(MQTT.client)

            ##TEMPORARY##
            ip = urllib.request.urlopen("https://api.ipify.org").read().decode('utf-8')
            await self.send(
                json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.SystemIP,
                        {"data": ip})
                )
            )
            ####

            # Send the state data that we already posses
            await self.send(json.dumps(ws_mqtt_state()))
            await self.send(json.dumps(ws_blackbox_state()))

    async def disconnect(self, close_code):
        for group in system_info:
            await self.channel_layer.group_discard(system_info[group], self.channel_name)

        print("WS {{Staff}} <SysStatus> -> {user} disconnected. Code: {code}".format(
            user=str(self.scope["user"]),
            code=close_code))

    async def receive(self, text_data):
        await StaffCommandDecoder.decode(self, text_data)

    async def component_log(self, event):
        '''Handles the "component.log" event before we send it out.'''
        await self.send(json.dumps(event))

    async def system_status(self, event):
        '''Handles the "system.status" event before we send it out.'''
        await self.send(json.dumps(event))

    async def update_state(self, event):
        '''Handles the "update.state" event before we send it out.'''
        await self.send(json.dumps(event))

    async def update_changelog(self, event):
        '''Handles the "update.changelog" event before we send it out.'''
        await self.send(json.dumps(event))

    async def update_start(self, event):
        '''Handles the "update.start" event before we send it out.'''
        await self.send(json.dumps(event))


class StaffZones(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_superuser:
            await self.accept()
            print("WS {{Staff}} <ZN> -> {user} connected.".format(user=str(self.scope["user"])))

            # Send the zones list after the user connects
            await self.send(
                json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.ZonesGet,
                        get_zones())
                )
            )

    async def disconnect(self, close_code):
        print("WS {{Staff}} <ZN> -> {user} disconnected. Code: {code}".format(
            user=str(self.scope["user"]),
            code=close_code))

    async def receive(self, text_data):
        await StaffCommandDecoder.decode(self, text_data)


class StaffCommandDecoder(AsyncWebsocketConsumer):

    async def decode(self, data):
        try:
            data = json.loads(data)

            if data["type"] == WSCMD.WSLSOC.UnregedListGet.value:
                await self.send(json.dumps(
                    WSCMD.new(WSCMD.WSLSOC.UnregedListGet,
                    MQTT.lsoc.getUnregisteredNodes())
                ))
            elif data["type"] == WSCMD.WSLSOC.NodeRegister.value:
                await self.send(json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.NodeRegister,
                        MQTT.lsoc.nodeRegistration(MQTT.client, data["data"]))
                ))
            elif data["type"] == WSCMD.WSLSOC.RegisteredListGet.value:
                await self.send(json.dumps(
                    WSCMD.new(WSCMD.WSLSOC.RegisteredListGet,
                    MQTT.lsoc.getRegisteredNodes())
                ))
            elif data["type"] == WSCMD.WSLSOC.NodeCommand.value:
                await self.send(json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.NodeCommand,
                        MQTT.lsoc.sendNodeCommand(MQTT.client, data["data"]))
                ))
            elif data["type"] == WSCMD.WSLSOC.NodeEdit.value:
                await self.send(json.dumps(
                    WSCMD.new_bare(
                        WSCMD.WSLSOC.NodeEdit,
                        MQTT.lsoc.updateNodeInfo(MQTT.client, data["data"]))
                ))
            elif data["type"] == WSCMD.WSLSOC.NECOStates.value:
                await MQTT.lsoc.NeutronCommunicator.requestStates(MQTT.client)
            elif data["type"] == WSCMD.WSLSOC.ComponentLog.value:
                await MQTT.lsoc.NeutronCommunicator.requestComponentLog(MQTT.client, data["data"])
            elif data["type"] == WSCMD.WSLSOC.UpdateCheck.value:
                await MQTT.lsoc.NeutronCommunicator.requestUpdateCheck(MQTT.client)
            elif data["type"] == WSCMD.WSLSOC.UpdateStart.value:
                await MQTT.lsoc.NeutronCommunicator.requestUpdateStart(MQTT.client)
            elif data["type"] == WSCMD.WSLSOC.ZonesGet.value:
                await self.send(
                    json.dumps(
                        WSCMD.new_bare(
                            WSCMD.WSLSOC.ZonesGet,
                            get_zones())
                    )
                )
            elif data["type"] == WSCMD.WSLSOC.ZoneAdd.value:
                await self.send(
                    json.dumps(
                        WSCMD.new_bare(
                            WSCMD.WSLSOC.ZoneAdd,
                            add_zone(data["data"]))
                    )
                )
            elif data["type"] == WSCMD.WSLSOC.ZoneRemove.value:
                await self.send(
                    json.dumps(
                        WSCMD.new_bare(
                            WSCMD.WSLSOC.ZoneRemove,
                            remove_zone(data["data"]))
                    )
                )
            elif data["type"] == WSCMD.WSLSOC.ZoneEdit.value:
                await self.send(
                    json.dumps(
                        WSCMD.new_bare(
                            WSCMD.WSLSOC.ZoneEdit,
                            edit_zone(data["data"]))
                    )
                )

            elif data["type"] == WSCMD.AccountManagement.AccountRegister.value:
                await self.send(json.dumps(register_account(data["data"])))
            elif data["type"] == WSCMD.AccountManagement.AccountEdit.value:
                await self.send(json.dumps(staff_edit_account(data["data"])))
            elif data["type"] == WSCMD.AccountManagement.AccountRemove.value:
                await self.send(json.dumps(staff_remove_account(data["data"])))

            elif data["type"] == WSCMD.WSLSOC.SystemShutdown.value or data["type"] == WSCMD.WSLSOC.SystemReboot.value:
                await self.send(json.dumps(MQTT.lsoc.system_shutdown_reboot(MQTT.client, data["type"])))

            else:
                print(f"WS {{Staff}} -> Unknown command received. {data}")
        except (KeyError, json.JSONDecodeError) as e:
            msg = "Could not process received command. Details: {}".format(e)
            print("WS {Staff} ERROR ->", msg)
            await self.send(json.dumps({"command": "Error", "data": msg}))


class UserCommandDecoder(AsyncWebsocketConsumer):

    async def decode(self, data):
        try:
            data = json.loads(data)

            if data["type"] == WSCMD.WSLSOC.ElementSet.value:
                try:
                    if await ACL.authorize_element_set(self.scope["user"], data["data"]):
                        await self.send(
                            json.dumps(
                                WSCMD.new(
                                    WSCMD.WSLSOC.ElementSet,
                                    MQTT.lsoc.set_element_state(MQTT.client, data["data"])
                                )
                            )
                        )
                except ACL.InvalidData:
                    await self.send(json.dumps({"command": WSCMD.WSLSOC.ElementSet.name, "data": {"status": False, "data": "Invalid data"}}))
            else:
                print("WS {User} -> Unknown command received. {cmd}".format(cmd=data))
        except (KeyError, json.JSONDecodeError) as e:
            msg = "Could not process received command. Details: {}".format(e)
            print("WS {User} ERROR ->", msg)
            await self.send(json.dumps({"command": "Error", "data": msg}))
