#!/usr/bin/env python3
"""
Script de test pour vérifier que l'API Swagger fonctionne correctement.
Ce script teste les endpoints principaux et vérifie la documentation Swagger.
"""

import requests
import json
import time
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000"
SWAGGER_URL = urljoin(BASE_URL, "/swagger/")
REDOC_URL = urljoin(BASE_URL, "/redoc/")
SWAGGER_JSON_URL = urljoin(BASE_URL, "/swagger.json")

def test_swagger_endpoints():
    """Teste les endpoints Swagger"""
    print("🔍 Test des endpoints Swagger...")
    
    # Test Swagger UI
    try:
        response = requests.get(SWAGGER_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
        else:
            print(f"❌ Swagger UI erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès Swagger UI: {e}")
    
    # Test ReDoc
    try:
        response = requests.get(REDOC_URL, timeout=10)
        if response.status_code == 200:
            print("✅ ReDoc accessible")
        else:
            print(f"❌ ReDoc erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès ReDoc: {e}")
    
    # Test Swagger JSON
    try:
        response = requests.get(SWAGGER_JSON_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Swagger JSON accessible")
            # Vérifier le contenu du JSON
            swagger_data = response.json()
            if 'info' in swagger_data:
                info = swagger_data['info']
                print(f"   📋 Titre: {info.get('title', 'N/A')}")
                print(f"   📋 Version: {info.get('version', 'N/A')}")
                print(f"   📋 Description: {info.get('description', 'N/A')[:100]}...")
            if 'paths' in swagger_data:
                paths = swagger_data['paths']
                print(f"   📋 Nombre d'endpoints: {len(paths)}")
        else:
            print(f"❌ Swagger JSON erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès Swagger JSON: {e}")

def test_api_endpoints():
    """Teste quelques endpoints de l'API"""
    print("\n🔍 Test des endpoints API...")
    
    # Test endpoint admin
    try:
        response = requests.get(urljoin(BASE_URL, "/admin/"), timeout=10)
        if response.status_code == 200:
            print("✅ Admin Django accessible")
        else:
            print(f"⚠️  Admin Django: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès Admin: {e}")
    
    # Test endpoints API (sans authentification)
    api_endpoints = [
        "/api/solar/battery/all",
        "/api/solar/panneau/all",
        "/api/solar/prise/all",
        "/api/solar/modules/all",
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(urljoin(BASE_URL, endpoint), timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403 sont normaux sans auth
                print(f"✅ {endpoint} - {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Erreur: {e}")

def test_swagger_schema():
    """Teste la structure du schéma Swagger"""
    print("\n🔍 Test de la structure Swagger...")
    
    try:
        response = requests.get(SWAGGER_JSON_URL, timeout=10)
        if response.status_code == 200:
            swagger_data = response.json()
            
            # Vérifier les sections principales
            required_sections = ['openapi', 'info', 'paths']
            for section in required_sections:
                if section in swagger_data:
                    print(f"✅ Section {section} présente")
                else:
                    print(f"❌ Section {section} manquante")
            
            # Vérifier les applications dans les paths
            paths = swagger_data.get('paths', {})
            expected_apps = ['battery', 'panneau', 'prise', 'modules', 'users']
            
            for app in expected_apps:
                app_paths = [path for path in paths.keys() if f'/api/solar/{app}/' in path]
                if app_paths:
                    print(f"✅ Application {app}: {len(app_paths)} endpoints")
                else:
                    print(f"⚠️  Application {app}: aucun endpoint trouvé")
            
            # Vérifier les méthodes HTTP
            http_methods = set()
            for path, methods in paths.items():
                http_methods.update(methods.keys())
            
            print(f"✅ Méthodes HTTP supportées: {', '.join(sorted(http_methods))}")
            
        else:
            print(f"❌ Impossible de récupérer le schéma Swagger: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test schéma: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test de l'API Solar avec Swagger")
    print("=" * 50)
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(3)
    
    # Tests
    test_swagger_endpoints()
    test_api_endpoints()
    test_swagger_schema()
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")
    print("\n📖 Pour accéder à la documentation:")
    print(f"   • Swagger UI: {SWAGGER_URL}")
    print(f"   • ReDoc: {REDOC_URL}")
    print(f"   • JSON Schema: {SWAGGER_JSON_URL}")

if __name__ == "__main__":
    main() 