#!/usr/bin/env python3
"""
Script pour compléter automatiquement l'ajout des décorateurs Swagger manquants
à toutes les vues Django REST Framework du projet solar_backend.
"""

import os
import re
from pathlib import Path

def add_swagger_decorators_to_remaining_views():
    """Ajoute les décorateurs Swagger manquants aux vues restantes"""
    
    # Applications à traiter
    apps = ['report', 'subscription']
    
    for app in apps:
        views_file = Path(f"{app}/views.py")
        if views_file.exists():
            print(f"Traitement de {views_file}...")
            
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ajouter les décorateurs aux classes APIView restantes
            content = add_decorators_to_api_view_classes(content, app)
            
            # Sauvegarder le fichier modifié
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {views_file} traité avec succès")

def add_decorators_to_api_view_classes(content, app_name):
    """Ajoute les décorateurs Swagger aux classes APIView"""
    
    # Patterns pour identifier les classes APIView sans décorateurs
    patterns = {
        'ReportAPIView': {
            'post': {
                'description': "Crée un nouveau rapport",
                'request_body': {
                    'required': ['description', 'priority', 'user', 'closed'],
                    'properties': {
                        'description': 'Description du rapport',
                        'priority': 'Priorité du rapport',
                        'user': 'ID de l\'utilisateur',
                        'closed': 'Statut de fermeture du rapport'
                    }
                },
                'responses': {
                    201: 'ReportSerializer',
                    400: 'Données manquantes',
                    500: 'Internal Server Error'
                }
            },
            'get': {
                'description': "Récupère un rapport par son ID",
                'manual_parameters': ['report_id'],
                'responses': {
                    200: 'ReportSerializer',
                    404: 'Rapport non trouvé',
                    500: 'Internal Server Error'
                }
            },
            'put': {
                'description': "Met à jour un rapport par son ID",
                'manual_parameters': ['report_id'],
                'request_body': {
                    'properties': {
                        'description': 'Description du rapport',
                        'priority': 'Priorité du rapport',
                        'closed': 'Statut de fermeture du rapport'
                    }
                },
                'responses': {
                    200: 'ReportSerializer',
                    404: 'Rapport non trouvé',
                    500: 'Internal Server Error'
                }
            },
            'delete': {
                'description': "Supprime un rapport par son ID",
                'manual_parameters': ['report_id'],
                'responses': {
                    204: 'Rapport supprimé avec succès',
                    404: 'Rapport non trouvé',
                    500: 'Internal Server Error'
                }
            }
        },
        'SubscriptionAPIView': {
            'post': {
                'description': "Crée un nouvel abonnement",
                'request_body': {
                    'required': ['user_id', 'name'],
                    'properties': {
                        'user_id': 'ID de l\'utilisateur',
                        'name': 'Nom de l\'abonnement',
                        'stockage_ensuel': 'Stockage mensuel',
                        'assistance': 'Assistance',
                        'entretien': 'Entretien',
                        'monitoring': 'Monitoring',
                        'remote_control': 'Contrôle à distance',
                        'planing': 'Planification',
                        'alert': 'Alertes'
                    }
                },
                'responses': {
                    201: 'SubscriptionSerializer',
                    400: 'Données manquantes',
                    500: 'Internal Server Error'
                }
            },
            'get': {
                'description': "Récupère un abonnement par son ID",
                'manual_parameters': ['sub_id'],
                'responses': {
                    200: 'SubscriptionSerializer',
                    404: 'Abonnement non trouvé',
                    500: 'Internal Server Error'
                }
            },
            'put': {
                'description': "Met à jour un abonnement par son ID",
                'manual_parameters': ['sub_id'],
                'request_body': {
                    'properties': {
                        'name': 'Nom de l\'abonnement',
                        'stockage_ensuel': 'Stockage mensuel',
                        'assistance': 'Assistance',
                        'entretien': 'Entretien',
                        'monitoring': 'Monitoring',
                        'remote_control': 'Contrôle à distance',
                        'planing': 'Planification',
                        'alert': 'Alertes'
                    }
                },
                'responses': {
                    200: 'SubscriptionSerializer',
                    404: 'Abonnement non trouvé',
                    500: 'Internal Server Error'
                }
            },
            'delete': {
                'description': "Supprime un abonnement par son ID",
                'manual_parameters': ['sub_id'],
                'responses': {
                    204: 'Abonnement supprimé avec succès',
                    404: 'Abonnement non trouvé',
                    500: 'Internal Server Error'
                }
            }
        }
    }
    
    # Appliquer les décorateurs pour chaque classe
    for class_name, methods in patterns.items():
        for method_name, config in methods.items():
            decorator = generate_swagger_decorator(method_name, config, app_name)
            
            # Trouver la méthode et ajouter le décorateur
            pattern = rf'(\s+)def {method_name}\(self, request'
            replacement = rf'{decorator}\n\1def {method_name}(self, request'
            
            content = re.sub(pattern, replacement, content)
    
    return content

def generate_swagger_decorator(method_name, config, app_name):
    """Génère un décorateur Swagger basé sur la configuration"""
    
    decorator = f"""    @swagger_auto_schema(
        operation_description="{config['description']}",
"""
    
    # Ajouter les paramètres manuels
    if 'manual_parameters' in config:
        decorator += "        manual_parameters=[\n"
        for param in config['manual_parameters']:
            decorator += f"""            openapi.Parameter(
                '{param}',
                openapi.IN_PATH,
                description="Identifiant unique du {param.replace('_', ' ')}",
                type=openapi.TYPE_STRING,
                required=True
            ),\n"""
        decorator += "        ],\n"
    
    # Ajouter le request_body
    if 'request_body' in config:
        decorator += f"""        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
"""
        if 'required' in config['request_body']:
            decorator += f"""            required={config['request_body']['required']},
"""
        decorator += "            properties={\n"
        for prop, desc in config['request_body']['properties'].items():
            decorator += f"""                '{prop}': openapi.Schema(type=openapi.TYPE_STRING, description='{desc}'),\n"""
        decorator += "            }\n        ),\n"
    
    # Ajouter les réponses
    decorator += "        responses={\n"
    for status_code, response in config['responses'].items():
        if isinstance(response, str) and 'Serializer' in response:
            decorator += f"""            {status_code}: {response},\n"""
        else:
            decorator += f"""            {status_code}: openapi.Response('{response}'),\n"""
    decorator += "        }\n    )"
    
    return decorator

def main():
    """Fonction principale"""
    print("🚀 Complétion des décorateurs Swagger manquants")
    print("=" * 50)
    
    # Changer vers le répertoire du projet
    os.chdir(Path(__file__).parent)
    
    # Ajouter les décorateurs manquants
    add_swagger_decorators_to_remaining_views()
    
    print("\n" + "=" * 50)
    print("🎉 Complétion terminée!")
    print("\n📋 Résumé des actions effectuées:")
    print("   • Ajout des décorateurs Swagger aux classes APIView restantes")
    print("   • Documentation complète des endpoints")
    print("   • Amélioration de la documentation Swagger")

if __name__ == "__main__":
    main() 