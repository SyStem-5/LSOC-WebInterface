from channels.generic.websocket import AsyncWebsocketConsumer

import json

from project01.system_scripts.mqtt_connection import ws_superuser_groups, ws_normaluser_groups

class DefaultConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
            print("WS: User connected.")

    async def disconnect(self, close_code):
        print("WS: User: "+ str(self.scope["user"]) +" disconnected. Code:", close_code)

    async def receive(self, text_data):
        print("WS: User: "+ str(self.scope["user"]) +" data received:", text_data)

class SuperuserConsumer(AsyncWebsocketConsumer):

    groups = ['node_state']

    async def connect(self):
        if self.scope["user"].is_superuser:
            await self.accept()
            await self.channel_layer.group_add(ws_superuser_groups[0], self.channel_name)
            print("WS: Superuser: "+ str(self.scope["user"]) +" connected.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(ws_superuser_groups[0], self.channel_name)
        print("WS: Superuser: "+ str(self.scope["user"]) +" disconnected. Code:", close_code)

    async def receive(self, text_data):
        print("WS: Superuser: "+ str(self.scope["user"]) +" data received:", text_data)

    async def node_state(self, event):
        # Handles the "node.state" event when it's sent to us.
        await self.send(text_data=str(event))