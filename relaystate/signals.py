# Django
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
# models
from battery.models import BatteryRelaiState
from panneau.models import PanneauRelaiState
from prise.models import PriseRelaiState

# signale
def _send_relay_state(module_id: str, payload: dict):
    channel_layer = get_channel_layer()
    group_name = f"relaystate_{module_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "relay_state",  # Appelera relay_state() dans RelayStateConsumer
            "data": payload,
        },
    )


@receiver(post_save, sender=BatteryRelaiState)
def battery_relay_updated(sender, instance: BatteryRelaiState, created, **kwargs):
    """
    Déclenché à CHAQUE modification du BatteryRelaiState.
    """
    module_id = instance.battery.module.id

    payload = {
        "component_type": "battery",
        "id": str(instance.id),
        "battery_id": str(instance.battery.id),
        "module_id": str(module_id),

        "active": instance.active,
        "state": instance.state,
        "couleur": instance.couleur,
        "valeur": instance.valeur,

        "updatedAt": instance.updatedAt.isoformat(timespec="seconds"),
    }

    _send_relay_state(module_id, payload)


@receiver(post_save, sender=PanneauRelaiState)
def panneau_relay_updated(sender, instance: PanneauRelaiState, created, **kwargs):
    module_id = instance.panneau.module.id

    payload = {
        "component_type": "panneau",
        "id": str(instance.id),
        "panneau_id": str(instance.panneau.id),
        "module_id": str(module_id),

        "active": instance.active,
        "state": instance.state,
        "couleur": instance.couleur,
        "valeur": instance.valeur,

        "updatedAt": instance.updatedAt.isoformat(timespec="seconds"),
    }

    _send_relay_state(module_id, payload)


@receiver(post_save, sender=PriseRelaiState)
def prise_relay_updated(sender, instance: PriseRelaiState, created, **kwargs):
    module_id = instance.prise.module.id

    payload = {
        "component_type": "prise",
        "id": str(instance.id),
        "prise_id": str(instance.prise.id),
        "module_id": str(module_id),

        "active": instance.active,
        "state": instance.state,
        "couleur": instance.couleur,
        "valeur": instance.valeur,

        "updatedAt": instance.updatedAt.isoformat(timespec="seconds"),
    }

    _send_relay_state(module_id, payload)
