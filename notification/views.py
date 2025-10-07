import logging

from rest_framework import status
# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

# django
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime, timedelta

# Notif
from .models import Notification
from users.models import ProfilUser


# Battery
from battery.models import Battery
from battery.models import BatteryData
# from battery.models import BatteryPlanning
# from battery.models import BatteryReference
# from battery.models import BatteryRelaiState

# prise
# from prise.models import Prise
from prise.models import PriseData

# panneau
from panneau.models import PanneauData

# serializer
from .serializers import NotificationSerializer
from panneau.serializers import PanneauDataSimpleSerializer

logger = logging.getLogger(__name__)



def create_notification_serializer(user_id,name,message):
    notif = Notification.objects.create(
        user_id=user_id,
        fonction=name,
        message=message,
    )
    serializer = NotificationSerializer(notif,many=False).data
    return serializer


def send_websocket_notification(user_id, data_notif):
    """
    Envoie une notification via WebSocket à l'utilisateur.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notification_{user_id}",
        {
            "type": "notification_message",
            "message": data_notif,
        },
    )
    

# create notification
@api_view(["POST"])
def  create_notification(request):
    user_id = request.data.get("user_id")
    fonction = request.data.get("fonction")
    message = request.data.get("message")
    
    user = get_object_or_404(ProfilUser, id=user_id)


    notif = Notification.objects.create(
        user=user,
        fonction=fonction,
        message=message,
    )
    serializer = NotificationSerializer(notif,many=False)
    # notification to socket
    send_websocket_notification(user_id, serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
@swagger_auto_schema(
    method='put',
    operation_description="Marque une notification comme lue",
    manual_parameters=[
        openapi.Parameter(
            'id_notif',
            openapi.IN_PATH,
            description="Identifiant unique de la notification",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: NotificationSerializer,
        404: openapi.Response('Notification non trouvée'),
        500: 'Internal Server Error'
    }
)
@api_view(["PUT"])
# @permission_classes([IsAuthenticated])
def read_notification(request,id_notif):
    try:
        notif = Notification.objects.get(id=id_notif)
        notif.read=True
        notif.save()
        serializer = NotificationSerializer(notif, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({"message":"notification not found"},status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='delete',
    operation_description="Supprime une notification",
    manual_parameters=[
        openapi.Parameter(
            'id_notif',
            openapi.IN_PATH,
            description="Identifiant unique de la notification",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        204: 'Notification supprimée avec succès',
        404: openapi.Response('Notification non trouvée'),
        500: 'Internal Server Error'
    }
)
@api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
def delete_notification(request,id_notif):
    try:
        notif = Notification.objects.get(id=id_notif)
        notif.delete()
        return Response({"message":"notification est supprimer"}, status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response({"message":"notification not found"},status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='put',
    operation_description="Marque toutes les notifications d'un utilisateur comme lues",
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description="Identifiant unique de l'utilisateur",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: NotificationSerializer(many=True),
        500: 'Internal Server Error'
    }
)
@api_view(["PUT"])
# @permission_classes([IsAuthenticated])
def read_all_notification(request,user_id):
    notif_data = Notification.objects.filter(user__id=user_id).order_by("-createdAt")
    for notif in notif_data:
        notif["read"]=True
        notif.save()
    serializer = NotificationSerializer(notif_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Récupère toutes les notifications d'un utilisateur",
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description="Identifiant unique de l'utilisateur",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: NotificationSerializer(many=True),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_by_user_notification(request,user_id):
    notif = Notification.objects.filter(user__id=user_id).order_by("-createdAt")
    serializer = NotificationSerializer(notif, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='delete',
    operation_description="Supprime toutes les notifications d'un utilisateur",
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description="Identifiant unique de l'utilisateur",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Notifications supprimées avec succès'),
        404: openapi.Response('Aucune notification trouvée'),
        500: 'Internal Server Error'
    }
)
@api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
def delete_all_by_user_notification(request,user_id):
  # Filtre les notifications par utilisateur
    notif_queryset = Notification.objects.filter(user__id=user_id)

    # Si aucune notification n'existe, renvoie un message approprié
    if not notif_queryset.exists():
        return Response(
            {"message": "Aucune notification trouvée pour cet utilisateur."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Supprime les notifications
    deleted_count = notif_queryset.delete()[0]  # `delete()` renvoie un tuple (num_deleted, _)
    return Response(
        {"message": f"Suppression réussie. {deleted_count} notification(s) supprimée(s)."},
        status=status.HTTP_200_OK,
    )
# ===============================================BATTERY =================================
# Courant
@receiver(post_save, sender=BatteryData)
def notify_courant_status(sender, instance, created, **kwargs):
    """
    Gère les notifications liées au courant.
    """
    if not created:
        return

    user_id = instance.battery.module.user.id
    courant = float(instance.courant or 0)
    message = None

    if courant == 0:
        message = "Aucune charge branchée."
    elif courant > 0:
        message = "Déchargement de la batterie."

    if message:
        data_notif = create_notification_serializer(user_id,"Courant", message)
        send_websocket_notification(user_id, data_notif)

# Puissance
@receiver(post_save, sender=BatteryData)
def notify_puissance_status(sender, instance, created, **kwargs):
    """
    Gère les notifications liées à la puissance.
    """
    if not created:
        return

    user_id = instance.battery.module.user.id
    puissance = float(instance.puissance or 0)
    capacity = float(instance.battery.puissance or 0)
    message = None

    if capacity > 0:
        if puissance >= 0.9 * capacity:
            message = (
                "Attention ! La puissance énergétique est très élevée. "
                "Veuillez réduire la puissance totale utilisée pour préserver votre batterie."
            )
        elif puissance <= 0.2 * capacity:
            message = (
                "Félicitations ! Vous utilisez moins de puissance d'énergie, vous réalisez des économies d'énergie."
            )
        elif puissance == 0:
            # Condition pour une puissance égale à 0 pendant 1h30
            time_since_last_change = datetime.now() - instance.createdAt
            if time_since_last_change >= timedelta(hours=1.5):
                message = "Pourquoi ne pas utiliser votre batterie ? Nous sommes là pour vous aider à mieux le gérer."

    if message:
        data_notif = create_notification_serializer(user_id,"Puissance", message)
        send_websocket_notification(user_id, data_notif)

# Consommation / Capacité
@receiver(post_save, sender=BatteryData)
def notify_consumption_status(sender, instance, created, **kwargs):
    """
    Gère les notifications liées à la consommation de la batterie.
    """
    if not created:
        return

    user_id = instance.battery.module.user.id
    capacity = float(instance.battery.puissance or 0)
    consumption = float(instance.energy or 0)  # Exemple, ajustez selon vos champs
    message = None

    # Notifications pour consommation dépassant 10% de la capacité en 1h
    if capacity > 0 and consumption > 0.1 * capacity:
        message = (
            "Vous avez consommé trop d'énergie en peu de temps. "
            "Veuillez respecter un timing raisonnable pour éviter des dommages à votre matériel."
        )
    elif capacity > 0 and consumption <= 0.1 * capacity:
        message = (
            "Bravo ! Votre consommation est optimale et préserve votre matériel. Continuez ainsi !"
        )

    # Notification quotidienne (fin de journée)
    if datetime.now().hour == 23 and datetime.now().minute == 59:
        message = f"Aujourd'hui, vous avez consommé un total de {consumption} Ah."

    if message:
        data_notif = create_notification_serializer(user_id,"Consommation", message)
        send_websocket_notification(user_id, data_notif)

# notification for new battery data
@receiver(post_save, sender=BatteryData)
def notify_new_BatteryData(sender, instance, created, **kwargs):
    if not created:
        return  
    

    battery = instance.battery
    module = battery.module
    user_id = module.user.id
    # notif
    data_notif = None
    
    # Paramètres utilisateur (ajuster selon vos modèles si nécessaire)
    tension_nominale = 12  # Par défaut, récupérer cela depuis le modèle utilisateur
    # Exemple : tension_nominale = user.settings.tension_nominale
    tension_actuelle = float(instance.tension) if instance.tension else 0.0

    # Messages de notification
    message = None
    if tension_actuelle == 0:
        message = "Vérifiez si votre batterie est correctement branchée."
    elif tension_actuelle > 0:
        message = "La batterie est branchée (passage de 0 à une valeur différente de 0)."


    # Notifications spécifiques aux tensions nominales
    if tension_nominale == 12:
        if tension_actuelle == 10.5:
            message = "Attention ! La tension de votre batterie est faible."

        elif tension_actuelle == 14.8:
            message = (
                "Votre batterie atteint sa tension maximale. "
                "Si elle dépasse 14,8V, nous vous conseillons d'ajuster le seuil dans les paramètres pour éviter des dommages."
            )

    elif tension_nominale == 24:
        if tension_actuelle == 21.6:
            message = "Attention ! La tension de votre batterie est faible."

        elif tension_actuelle == 28.8:
            message = (
                "Votre batterie atteint sa tension maximale. "
                "Si elle dépasse 28,8V, ajustez le seuil dans les paramètres."
            )

    elif tension_nominale == 48:
        if tension_actuelle == 39.0:
            message = "Attention ! La tension de votre source est faible."

        elif tension_actuelle == 54.6:
            message = (
                "Votre batterie atteint sa tension maximale. "
                "Si elle dépasse 54,6V, ajustez le seuil dans les paramètres."
            )
            
 # Si un message est défini, envoyer la notification
    if message:
        data_notif = create_notification_serializer(user_id, "Tension", message)
        send_websocket_notification(user_id, data_notif)


@receiver(post_save, sender=BatteryData)
def notify_battery_send_reel_data(sender, instance, created, **kwargs):
    if not created:  # Ne notifier que lors de la création d'une nouvelle entrée
        return

    # send    
    user_id = instance.battery.module.user.id

     # Construire formatted_entry (même format que votre API)
    created_at = getattr(instance, "createdAt", timezone.now())
    formatted_entry = {
        "timestamp": created_at.isoformat(),
        "hour_label": created_at.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        "energy": float(instance.energy or 0),
        "pourcentage": float(instance.pourcentage or 0),
    }
    
    if not user_id :  # Si l'utilisateur n'est pas défini, ne pas continuer
        return
    send_websocket_notification(user_id , formatted_entry)


# ===================================================PRISE =================================

@receiver(post_save, sender=PriseData)
def notify_prise_data(sender, instance, created, **kwargs):
    if not created:  # Ne notifier que lors de la création d'une nouvelle entrée
        return

    user_id = instance.prise.module.user.id
    if not user_id:  # Si l'utilisateur n'est pas défini, ne pas continuer
        return

    messages = []

    # Vérification de la tension
    if instance.tension:
        tension = float(instance.tension)
        if tension == 0:
            messages.append("Aucun appareil détecté. Il semble que la prise soit déconnectée ou l'interrupteur soit éteint. Veuillez vérifier vos branchements ou allumer l'interrupteur.")
        elif tension > 0 and tension < 200:
            messages.append("Attention ! Une baisse de tension a été détectée. Il est recommandé d'installer un onduleur pour protéger votre matériel.")
        elif tension >= 200 and tension < 230:
            messages.append("Un appareil a été détecté et branché avec succès. Vous pouvez désormais planifier son utilisation via les paramètres de planification.")
        elif tension >= 230:
            messages.append("Attention ! Une surtension a été détectée. Il est recommandé d'installer un onduleur pour éviter d'endommager votre matériel.")

    # Vérification du courant
    if instance.courant:
        courant = float(instance.courant)
        if courant == 0:
            messages.append("Aucun appareil détecté sur cette source. Veuillez vérifier si votre matériel est correctement branché.")
        elif courant > 0:
            messages.append("Un appareil a été détecté et le branchement est réussi.")

    # Vérification de la puissance
    if instance.puissance:
        puissance = float(instance.puissance)
        messages.append(f"Votre appareil consomme environ {puissance} kW.")

    # Vérification de la consommation
    if instance.consomation:
        consomation = float(instance.consomation)
        messages.append(f"Votre appareil consomme {consomation} kWh d'énergie.")

    # Ajout des notifications au système
    for message in messages:
        data_notif = create_notification_serializer(user_id, "Prise", message)
        send_websocket_notification(user_id, data_notif)



# envoyer le donne reelle dans 
@receiver(post_save, sender=PriseData)
def notify_prise_send_reel_data(sender, instance, created, **kwargs):
    if not created:  # Ne notifier que lors de la création d'une nouvelle entrée
        return

    # send    
    user_id = instance.prise.module.user.id

     # Construire formatted_entry (même format que votre API)
    created_at = getattr(instance, "createdAt", timezone.now())
    formatted_entry = {
        "timestamp": created_at.isoformat(),
        "hour_label": created_at.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        "consommation": float(instance.consomation or 0),
    }
    
    if not user_id :  # Si l'utilisateur n'est pas défini, ne pas continuer
        return
    send_websocket_notification(user_id , formatted_entry)


# ==================================================PANNEAU SOLAR =================================
@receiver(post_save, sender=PanneauData)
def notify_panneau_data(sender, instance, created, **kwargs):
    if not created:  # Ne notifier que lors de la création d'une nouvelle entrée
        return


    panneau = instance.panneau
    user_id = panneau.module.user.id
    if not user_id:  # Si l'utilisateur n'est pas défini, ne pas continuer
        return
    

    messages = []

    # Production d'energie anormale
    if instance.production:
        production = float(instance.production)
        puissance_nominale = 300  # Exemple: Valeur par défaut pour un panneau de 300W
        heures_ensoleillement = 5  # Valeur par défaut pour Madagascar
        production_moyenne = (puissance_nominale * heures_ensoleillement) / 1000  # En kWh
        seuil_critique = (production_moyenne * 30) / 100

        if production == 0:
            messages.append(
                "Attention : Aucune production solaire détectée en plein jour. Vérifiez votre installation pour une éventuelle panne ou un problème majeur."
            )
        elif production < seuil_critique:
            messages.append(
                "Une baisse de production des panneaux solaires est observée au cours de la journée. Cela peut être dû à un ensoleillement insuffisant ou à l'accumulation de particules de poussière réduisant leur efficacité."
            )

    # Problèmes de connectivité
    if instance.updatedAt and instance.createdAt:
        delta_seconds = (instance.updatedAt - instance.createdAt).total_seconds()
        if delta_seconds > 3600:
            messages.append("Perte de communication détectée (>1h) avec le panneau.")
 

    # Température inhabituelle (si un capteur de température est intégré)
    if hasattr(instance, 'temperature') and instance.temperature:
        temperature = float(instance.temperature)
        if temperature >= 70:
            messages.append(
                "Attention : Température inhabituelle détectée sur le panneau solaire, risque de points chauds. Vérifiez rapidement pour éviter tout dommage."
            )

    # Accumulation de poussière ou saleté (si un capteur est intégré)
    if hasattr(instance, 'dust_level') and instance.dust_level:
        dust_level = float(instance.dust_level)
        if dust_level > 70:  # Exemple de seuil
            messages.append(
                "Attention : Une accumulation importante de poussière, de saleté ou de neige a été détectée sur le panneau solaire. Nettoyez pour optimiser la production."
            )

    # Envoi des notifications    
    for msg in messages:        
        try:
            data_notif = create_notification_serializer(user_id, "Panneau", msg)
        except Exception:
            data_notif = None

        if data_notif is not None:
            try:
                send_websocket_notification(user_id, data_notif)
            except Exception:
                logger.exception("Erreur envoi websocket pour user %s", user_id)

# envoyer le donne reelle dans 
@receiver(post_save, sender=PanneauData)
def notify_panneau_send_reel_data(sender, instance, created, **kwargs):
    if not created:  # Ne notifier que lors de la création d'une nouvelle entrée
        return
    

    # send    
    panneau = instance.panneau
    user_id  = panneau.module.user.id

     # Construire formatted_entry (même format que votre API)
    created_at = getattr(instance, "createdAt", timezone.now())
    formatted_entry = {
        "timestamp": created_at.isoformat(),
        "hour_label": created_at.strftime("%H:%M"),
        "tension": float(instance.tension or 0),
        "puissance": float(instance.puissance or 0),
        "courant": float(instance.courant or 0),
        "production": float(instance.production or 0),
    }
    
    if not user_id :  # Si l'utilisateur n'est pas défini, ne pas continuer
        return
    send_websocket_notification(user_id , formatted_entry)
