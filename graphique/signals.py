# realtime/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from solar_backend.timezone_utils import (
    get_local_timezone,
    local_day_bounds,
    local_month_bounds,
    local_now,
    local_today,
)

from battery.models import BatteryData
from panneau.models import PanneauData
from prise.models import PriseData



def _send_module_data(module_id: str, payload: dict):
    channel_layer = get_channel_layer()
    group_name = f"module_{module_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "module_data",  # appelle module_data() du consumer
            "data": payload,
        },
    )


@receiver(post_save, sender=BatteryData)
def battery_data_created(sender, instance: BatteryData, created, **kwargs):
    if not created:
        return

    tz_tana = get_local_timezone()
    module_id = instance.battery.module.id

    created_at_utc = instance.createdAt
    created_at_local = created_at_utc.astimezone(tz_tana)

    payload = {
        "component_type": "battery",
        "source": "battery",  # pour compatibilité
        "id": instance.id,
        "battery_id": instance.battery.id,
        "module_id": module_id,
        "timestamp": created_at_local.isoformat(timespec="seconds"),
        "timestamp_utc": created_at_utc.astimezone(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "hour_label": created_at_local.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        "energy": float(instance.energy or 0),
        "pourcentage": float(instance.pourcentage or 0),
    }

    _send_module_data(module_id, payload)


@receiver(post_save, sender=PanneauData)
def panneau_data_created(sender, instance: PanneauData, created, **kwargs):
    if not created:
        return

    tz_tana = get_local_timezone()
    module_id = instance.panneau.module.id

    created_at_utc = instance.createdAt
    created_at_local = created_at_utc.astimezone(tz_tana)

    payload = {
        "component_type": "panneau",
        "source": "panneau",
        "id": instance.id,
        "panneau_id": instance.panneau.id,
        "module_id": module_id,
        "timestamp": created_at_local.isoformat(timespec="seconds"),
        "timestamp_utc": created_at_utc.astimezone(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "hour_label": created_at_local.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        "production": float(instance.production or 0),
    }

    _send_module_data(module_id, payload)


@receiver(post_save, sender=PriseData)
def prise_data_created(sender, instance: PriseData, created, **kwargs):
    if not created:
        return

    tz_tana = get_local_timezone()
    module_id = instance.prise.module.id

    created_at_utc = instance.createdAt
    created_at_local = created_at_utc.astimezone(tz_tana)

    payload = {
        "component_type": "prise",
        "source": "prise",
        "id": instance.id,
        "prise_id": instance.prise.id,
        "module_id": module_id,
        "timestamp": created_at_local.isoformat(timespec="seconds"),
        "timestamp_utc": created_at_utc.astimezone(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "hour_label": created_at_local.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        # ATTENTION : dans le modèle c'est "consomation"
        "consommation": float(instance.consomation or 0),
    }

    _send_module_data(module_id, payload)
