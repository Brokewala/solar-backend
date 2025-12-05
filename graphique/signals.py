# realtime/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from solar_backend.timezone_utils import get_local_timezone

from battery.models import BatteryData
from panneau.models import PanneauData
from prise.models import PriseData


def _send_module_data(module_id, payload: dict):
    """
    module_id peut être UUID ou str -> on le force en str
    """
    group_name = f"module_{str(module_id)}"
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "module_data",
            "data": payload,
        },
    )


@receiver(post_save, sender=BatteryData)
def battery_data_created(sender, instance: BatteryData, created, **kwargs):
    if not created:
        return

    tz_tana = get_local_timezone()
    # si FK est UUIDField → .battery.module_id peut être UUID
    module_id = instance.battery.module_id

    created_at_utc = instance.createdAt
    created_at_local = created_at_utc.astimezone(tz_tana)

    payload = {
        "component_type": "battery",
        "source": "battery",
        "id": str(instance.id),
        "battery_id": str(instance.battery_id),
        "module_id": str(module_id),
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
    module_id = instance.panneau.module_id

    created_at_utc = instance.createdAt
    created_at_local = created_at_utc.astimezone(tz_tana)

    payload = {
        "component_type": "panneau",
        "source": "panneau",
        "id": str(instance.id),
        "panneau_id": str(instance.panneau_id),
        "module_id": str(module_id),
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
    module_id = instance.prise.module_id

    created_at_utc = instance.createdAt
    created_at_local = created_at_utc.astimezone(tz_tana)

    payload = {
        "component_type": "prise",
        "source": "prise",
        "id": str(instance.id),
        "prise_id": str(instance.prise_id),
        "module_id": str(module_id),
        "timestamp": created_at_local.isoformat(timespec="seconds"),
        "timestamp_utc": created_at_utc.astimezone(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "hour_label": created_at_local.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        # modèle = consomation, API = consommation
        "consommation": float(instance.consomation or 0),
    }

    _send_module_data(module_id, payload)
