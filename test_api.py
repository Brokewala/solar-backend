#!/usr/bin/env python3
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_backend.settings')
django.setup()

from users.models import ProfilUser
from module.models import Modules
from battery.models import Battery, BatteryData
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData

def test_database_direct():
    """Test direct de la base de données"""
    print("🔍 Test direct de la base de données...")
    
    # Test utilisateur
    try:
        user = ProfilUser.objects.get(email="brokewala@gmail.com")
        print(f"✅ Utilisateur trouvé: {user.email}")
        print(f"   - Nom: {user.first_name} {user.last_name}")
        print(f"   - Actif: {user.status}")
        
        # Test module
        try:
            module = Modules.objects.get(user=user)
            print(f"✅ Module trouvé: {module.reference}")
            print(f"   - Identifiant: {module.identifiant}")
            print(f"   - Actif: {module.active}")
            
            # Test batterie
            try:
                battery = Battery.objects.get(module=module)
                print(f"✅ Batterie trouvée: {battery.marque}")
                print(f"   - Puissance: {battery.puissance}W")
                print(f"   - Voltage: {battery.voltage}V")
                
                # Test données batterie
                battery_data_count = BatteryData.objects.filter(battery=battery).count()
                print(f"✅ Données batterie: {battery_data_count} entrées")
                
                if battery_data_count > 0:
                    latest_data = BatteryData.objects.filter(battery=battery).latest('createdAt')
                    print(f"   - Dernière donnée: {latest_data.pourcentage}% - {latest_data.puissance}W")
                
            except Battery.DoesNotExist:
                print("❌ Aucune batterie trouvée")
            
            # Test panneau
            try:
                panneau = Panneau.objects.get(module=module)
                print(f"✅ Panneau trouvé: {panneau.marque}")
                print(f"   - Puissance: {panneau.puissance}W")
                
                # Test données panneau
                panneau_data_count = PanneauData.objects.filter(panneau=panneau).count()
                print(f"✅ Données panneau: {panneau_data_count} entrées")
                
                if panneau_data_count > 0:
                    latest_data = PanneauData.objects.filter(panneau=panneau).latest('createdAt')
                    print(f"   - Dernière donnée: {latest_data.puissance}W - {latest_data.production}")
                
            except Panneau.DoesNotExist:
                print("❌ Aucun panneau trouvé")
            
            # Test prise
            try:
                prise = Prise.objects.get(module=module)
                print(f"✅ Prise trouvée: {prise.name}")
                print(f"   - Voltage: {prise.voltage}V")
                
                # Test données prise
                prise_data_count = PriseData.objects.filter(prise=prise).count()
                print(f"✅ Données prise: {prise_data_count} entrées")
                
                if prise_data_count > 0:
                    latest_data = PriseData.objects.filter(prise=prise).latest('createdAt')
                    print(f"   - Dernière donnée: {latest_data.puissance}W - {latest_data.consomation}")
                
            except Prise.DoesNotExist:
                print("❌ Aucune prise trouvée")
                
        except Modules.DoesNotExist:
            print("❌ Aucun module trouvé pour cet utilisateur")
            
    except ProfilUser.DoesNotExist:
        print("❌ Utilisateur non trouvé")

def test_authentication():
    """Test d'authentification directe"""
    print("\n🔐 Test d'authentification...")
    
    try:
        user = ProfilUser.objects.get(email="brokewala@gmail.com")
        
        # Test du mot de passe
        if user.check_password("broke2212916"):
            print("✅ Mot de passe correct")
        else:
            print("❌ Mot de passe incorrect")
            
        print(f"   - Utilisateur actif: {user.status}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
        
    except ProfilUser.DoesNotExist:
        print("❌ Utilisateur non trouvé pour l'authentification")

def test_api_endpoints():
    """Test des endpoints API"""
    print("\n🌐 Test des endpoints API...")
    
    base_url = "http://localhost:8001/api/solar"
    
    # Test de login
    login_data = {
        "email": "brokewala@gmail.com",
        "password": "broke2212916"
    }
    
    try:
        print("📡 Test de l'endpoint de login...")
        # Nous ne pouvons pas tester l'API HTTP car le serveur n'est pas accessible
        # Mais nous pouvons vérifier que les vues existent
        from users.views import loginAction
        print("✅ Vue de login trouvée")
        
        from module.views import get_one_module_by_user
        print("✅ Vue de module trouvée")
        
        from battery.views import get_all_battery
        print("✅ Vue de batterie trouvée")
        
        from panneau.views import get_all_panneau
        print("✅ Vue de panneau trouvée")
        
        from prise.views import get_all_Prise
        print("✅ Vue de prise trouvée")
        
    except Exception as e:
        print(f"❌ Erreur lors du test des vues: {e}")

def main():
    print("🚀 Test complet du backend Solar...")
    print("=" * 50)
    
    test_database_direct()
    test_authentication()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")

if __name__ == "__main__":
    main()
