# realtime/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from battery.models import Battery, BatteryRelaiState
from panneau.models import Panneau, PanneauRelaiState
from prise.models import Prise, PriseRelaiState


class RelayStateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.module_id = self.scope["url_route"]["kwargs"]["module_id"]
        self.room_group_name = f"relaystate_{self.module_id}"

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

    async def receive(self, text_data=None, bytes_data=None):
        """
        Reçoit des commandes depuis le client React Native.

        JSON attendu :
        {
          "component_type": "battery" | "panneau" | "prise",
          "action": "toggle" | "on" | "off"
        }
        """
        if not text_data:
            return
        
        print("===========text_data============",text_data)

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        component_type = payload.get("component_type")
        action = payload.get("action", "toggle")

        if component_type not in ("battery", "panneau", "prise"):
            return

        # On exécute la logique DB en thread sync via sync_to_async
        if component_type == "battery":
            await self._handle_battery_action(action)
        elif component_type == "panneau":
            await self._handle_panneau_action(action)
        elif component_type == "prise":
            await self._handle_prise_action(action)

        # Important : on ne renvoie rien ici, le changement sera
        # broadcast via les signaux post_save -> WebSocket

    # ==========================
    #   Helpers DB (sync)
    # ==========================
    @sync_to_async
    def _handle_battery_action(self, action: str):
        try:
            battery = Battery.objects.get(module_id=self.module_id)
        except Battery.DoesNotExist:
            return

        relay, _ = BatteryRelaiState.objects.get_or_create(battery=battery)

        if action == "on":
            relay.active = True
            relay.couleur = "green"
            relay.state = "high"
            relay.valeur = "1"
        elif action == "off":
            relay.active = False
            relay.couleur = "red"
            relay.state = "low"
            relay.valeur = "0"
        else:  # toggle
            relay.active = not relay.active
            if relay.active:
                relay.couleur = "green"
                relay.state = "high"
                relay.valeur = "1"
            else:
                relay.couleur = "red"
                relay.state = "low"
                relay.valeur = "0"

        relay.save()  # déclenche le signal → push WS

    @sync_to_async
    def _handle_panneau_action(self, action: str):
        try:
            panneau = Panneau.objects.get(module_id=self.module_id)
        except Panneau.DoesNotExist:
            return

        relay, _ = PanneauRelaiState.objects.get_or_create(panneau=panneau)

        if action == "on":
            relay.active = True
            relay.couleur = "green"
            relay.state = "high"
            relay.valeur = "1"
        elif action == "off":
            relay.active = False
            relay.couleur = "red"
            relay.state = "low"
            relay.valeur = "0"
        else:  # toggle
            relay.active = not relay.active
            if relay.active:
                relay.couleur = "green"
                relay.state = "high"
                relay.valeur = "1"
            else:
                relay.couleur = "red"
                relay.state = "low"
                relay.valeur = "0"

        relay.save()

    @sync_to_async
    def _handle_prise_action(self, action: str):
        try:
            prise = Prise.objects.get(module_id=self.module_id)
        except Prise.DoesNotExist:
            return

        relay, _ = PriseRelaiState.objects.get_or_create(prise=prise)

        if action == "on":
            relay.active = True
            relay.couleur = "green"
            relay.state = "high"
            relay.valeur = "1"
        elif action == "off":
            relay.active = False
            relay.couleur = "red"
            relay.state = "low"
            relay.valeur = "0"
        else:  # toggle
            relay.active = not relay.active
            if relay.active:
                relay.couleur = "green"
                relay.state = "high"
                relay.valeur = "1"
            else:
                relay.couleur = "red"
                relay.state = "low"
                relay.valeur = "0"

        relay.save()

    # ==========================
    #   Event push (depuis signaux)
    # ==========================
    async def relay_state(self, event):
        await self.send(text_data=json.dumps(event["data"]))
