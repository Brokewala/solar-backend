#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_backend.settings')
django.setup()

from users.models import ProfilUser
from module.models import Modules
from battery.models import Battery, BatteryData
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData
from solar_backend.timezone_utils import local_now

def add_and_check_daily_data():
    print("🧪 Test ajout et récupération des données journalières...")

    # Récupérer un utilisateur et son module
    user = ProfilUser.objects.first()
    if not user:
        print("❌ Aucun utilisateur trouvé")
        return
    module = Modules.objects.filter(user=user).first()
    if not module:
        print("❌ Aucun module trouvé")
        return

    # Batterie
    battery = Battery.objects.filter(module=module).first()
    if battery:
        BatteryData.objects.create(
            battery=battery,
            energy=1.5,
            tension=12.5,
            puissance=100,
            courant=8.0,
            pourcentage=80,
            createdAt=local_now()
        )
        data = BatteryData.objects.filter(battery=battery)
        print(f"✅ Batterie: {data.count()} données journalières")
    else:
        print("❌ Batterie non trouvée")

    # Panneau
    panneau = Panneau.objects.filter(module=module).first()
    if panneau:
        PanneauData.objects.create(
            panneau=panneau,
            production=2.3,
            tension=18.0,
            puissance=120,
            courant=6.7,
            createdAt=local_now()
        )
        data = PanneauData.objects.filter(panneau=panneau)
        print(f"✅ Panneau: {data.count()} données journalières")
    else:
        print("❌ Panneau non trouvé")

    # Prise
    prise = Prise.objects.filter(module=module).first()
    if prise:
        PriseData.objects.create(
            prise=prise,
            consommation=0.8,
            tension=220.0,
            puissance=60,
            courant=0.3,
            createdAt=local_now()
        )
        data = PriseData.objects.filter(prise=prise)
        print(f"✅ Prise: {data.count()} données journalières")
    else:
        print("❌ Prise non trouvée")

if __name__ == "__main__":
    add_and_check_daily_data()
