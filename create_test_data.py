#!/usr/bin/env python3
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_backend.settings')
django.setup()

from users.models import ProfilUser
from module.models import Modules, ModulesInfo, ModulesDetail
from battery.models import Battery, BatteryData, BatteryPlanning, BatteryReference, BatteryRelaiState
from panneau.models import Panneau, PanneauData, PanneauPlanning, PanneauReference, PanneauRelaiState
from prise.models import Prise, PriseData, PrisePlanning, PriseReference, PriseRelaiState
from notification.models import Notification

def create_test_user():
    """Créer un utilisateur de test"""
    try:
        user = ProfilUser.objects.get(email="brokewala@gmail.com")
        print(f"Utilisateur existant trouvé: {user.email}")
    except ProfilUser.DoesNotExist:
        user = ProfilUser.objects.create_user(
            email="brokewala@gmail.com",
            password="broke2212916",
            first_name="Test",
            last_name="User",
            phone="+33123456789",
            adresse="123 Rue de la Paix",
            code_postal="75001",
            status=True
        )
        print(f"Utilisateur créé: {user.email}")

    return user

def create_test_module(user):
    """Créer un module de test"""
    try:
        module = Modules.objects.get(user=user)
        print(f"Module existant trouvé: {module.reference}")
    except Modules.DoesNotExist:
        module = Modules.objects.create(
            user=user,
            reference="SOL-001",
            identifiant="module_test_001",
            password="module123",
            active=True
        )
        print(f"Module créé: {module.reference}")

    return module

def create_test_battery(module):
    """Créer une batterie de test avec des données"""
    try:
        battery = Battery.objects.get(module=module)
        print(f"Batterie existante trouvée: {battery.marque}")
    except Battery.DoesNotExist:
        battery = Battery.objects.create(
            module=module,
            marque="Tesla Powerwall",
            puissance="5000",
            voltage="48"
        )
        print(f"Batterie créée: {battery.marque}")

    # Créer des données de batterie
    BatteryData.objects.filter(battery=battery).delete()
    for i in range(24):  # 24 heures de données
        BatteryData.objects.create(
            battery=battery,
            tension=str(48 + random.uniform(-2, 2)),
            puissance=str(random.uniform(1000, 4000)),
            courant=str(random.uniform(20, 80)),
            energy=str(random.uniform(2000, 5000)),
            pourcentage=str(random.uniform(20, 95))
        )

    print(f"Données de batterie créées: 24 entrées")
    return battery

def create_test_panneau(module):
    """Créer un panneau solaire de test avec des données"""
    try:
        panneau = Panneau.objects.get(module=module)
        print(f"Panneau existant trouvé: {panneau.marque}")
    except Panneau.DoesNotExist:
        panneau = Panneau.objects.create(
            module=module,
            marque="SunPower",
            puissance="300",
            voltage="24"
        )
        print(f"Panneau créé: {panneau.marque}")

    # Créer des données de panneau
    PanneauData.objects.filter(panneau=panneau).delete()
    for i in range(24):  # 24 heures de données
        # Simulation de production solaire (plus élevée en journée)
        hour = i
        if 6 <= hour <= 18:  # Journée
            base_power = random.uniform(100, 280)
        else:  # Nuit
            base_power = 0

        PanneauData.objects.create(
            panneau=panneau,
            tension=str(24 + random.uniform(-1, 1)),
            puissance=str(base_power),
            courant=str(base_power / 24 if base_power > 0 else 0),
            production=str(base_power * 1.2)
        )

    print(f"Données de panneau créées: 24 entrées")
    return panneau

def create_test_prise(module):
    """Créer une prise de test avec des données"""
    try:
        prise = Prise.objects.get(module=module)
        print(f"Prise existante trouvée: {prise.name}")
    except Prise.DoesNotExist:
        prise = Prise.objects.create(
            module=module,
            name="Prise Principale",
            voltage="220"
        )
        print(f"Prise créée: {prise.name}")

    # Créer des données de prise
    PriseData.objects.filter(prise=prise).delete()
    for i in range(24):  # 24 heures de données
        # Simulation de consommation (plus élevée en soirée)
        hour = i
        if 18 <= hour <= 23 or 6 <= hour <= 9:  # Heures de pointe
            base_power = random.uniform(800, 1500)
        elif 9 <= hour <= 18:  # Journée normale
            base_power = random.uniform(200, 800)
        else:  # Nuit
            base_power = random.uniform(50, 200)

        PriseData.objects.create(
            prise=prise,
            tension=str(220 + random.uniform(-5, 5)),
            puissance=str(base_power),
            courant=str(base_power / 220),
            consomation=str(base_power * 1.1)
        )

    print(f"Données de prise créées: 24 entrées")
    return prise

def create_test_notifications(user):
    """Créer des notifications de test"""
    notifications = [
        "Batterie faible: 25% de charge restante",
        "Production solaire optimale détectée",
        "Consommation élevée sur la prise principale",
        "Maintenance programmée dans 7 jours",
        "Nouveau record de production aujourd'hui!"
    ]

    Notification.objects.filter(user=user).delete()
    for i, message in enumerate(notifications):
        Notification.objects.create(
            user=user,
            message=message,
            read=i < 2  # Les 2 premières sont lues
        )

    print(f"Notifications créées: {len(notifications)} entrées")

def main():
    print("🚀 Création des données de test...")

    # Créer l'utilisateur
    user = create_test_user()

    # Créer le module
    module = create_test_module(user)

    # Créer les composants avec des données
    battery = create_test_battery(module)
    panneau = create_test_panneau(module)
    prise = create_test_prise(module)

    # Créer des notifications
    create_test_notifications(user)

    print("\n✅ Données de test créées avec succès!")
    print(f"📧 Email: {user.email}")
    print(f"🔑 Mot de passe: broke2212916")
    print(f"🏠 Module: {module.reference}")
    print(f"🔋 Batterie: {battery.marque}")
    print(f"☀️ Panneau: {panneau.marque}")
    print(f"🔌 Prise: {prise.name}")

if __name__ == "__main__":
    main()
