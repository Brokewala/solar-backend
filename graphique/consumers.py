# realtime/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ModuleDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.module_id = self.scope["url_route"]["kwargs"]["module_id"]
        self.room_group_name = f"module_{self.module_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Pas besoin de receive pour ce flux (on push seulement du backend -> client)
    async def receive(self, text_data=None, bytes_data=None):
        return

    # Event générique pour battery / panneau / prise
    async def module_data(self, event):
        """
        event = {
          "type": "module_data",
          "data": {...}  # contient source: "battery"/"panneau"/"prise"
        }
        """
        await self.send(text_data=json.dumps(event["data"]))
