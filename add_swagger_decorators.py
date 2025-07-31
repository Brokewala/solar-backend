#!/usr/bin/env python3
"""
Script pour ajouter automatiquement les décorateurs Swagger à toutes les vues Django REST Framework.
Ce script analyse les fichiers views.py et ajoute les décorateurs @swagger_auto_schema appropriés.
"""

import os
import re
from pathlib import Path

# Configuration des applications
APPS_CONFIG = {
    'battery': {
        'serializers': {
            'BatterySerializer': 'BatterySerializer',
            'BatteryDataSerializer': 'BatteryDataSerializer',
            'BatteryPlanningSerializer': 'BatteryPlanningSerializer',
            'BatteryRelaiStateSerializer': 'BatteryRelaiStateSerializer',
            'BatteryReferenceSerializer': 'BatteryReferenceSerializer',
            'BatteryAllSerializer': 'BatteryAllSerializer(many=True)',
        },
        'request_schemas': {
            'Battery': {
                'required': ['puissance', 'voltage', 'module', 'marque'],
                'properties': {
                    'puissance': 'Puissance de la batterie (en W ou kW)',
                    'voltage': 'Tension de la batterie (en V)',
                    'module': 'ID du module associé',
                    'marque': 'Marque du fabricant'
                }
            },
            'BatteryData': {
                'required': ['battery', 'tension', 'puissance', 'courant', 'energy', 'pourcentage'],
                'properties': {
                    'battery': 'ID de la batterie',
                    'tension': 'Tension actuelle (en V)',
                    'puissance': 'Puissance actuelle (en W)',
                    'courant': 'Courant actuel (en A)',
                    'energy': 'Énergie stockée (en Wh)',
                    'pourcentage': 'Pourcentage de charge (%)'
                }
            }
        }
    },
    'panneau': {
        'serializers': {
            'PanneauSerializer': 'PanneauSerializer',
            'PanneauDataSerializer': 'PanneauDataSerializer',
            'PanneauPlanningSerializer': 'PanneauPlanningSerializer',
            'PanneauRelaiStateSerializer': 'PanneauRelaiStateSerializer',
            'PanneauReferenceSerializer': 'PanneauReferenceSerializer',
            'PenneauAllSerializer': 'PenneauAllSerializer(many=True)',
        },
        'request_schemas': {
            'Panneau': {
                'required': ['puissance', 'voltage', 'module', 'marque'],
                'properties': {
                    'puissance': 'Puissance du panneau (en W ou kW)',
                    'voltage': 'Tension du panneau (en V)',
                    'module': 'ID du module associé',
                    'marque': 'Marque du fabricant'
                }
            }
        }
    },
    'prise': {
        'serializers': {
            'PriseSerializer': 'PriseSerializer',
            'PriseDataSerializer': 'PriseDataSerializer',
            'PrisePlanningSerializer': 'PrisePlanningSerializer',
            'PriseRelaiStateSerializer': 'PriseRelaiStateSerializer',
            'PriseReferenceSerializer': 'PriseReferenceSerializer',
            'PriseAllSerializer': 'PriseAllSerializer(many=True)',
        },
        'request_schemas': {
            'Prise': {
                'required': ['name', 'voltage', 'module'],
                'properties': {
                    'name': 'Nom de la prise électrique',
                    'voltage': 'Tension de la prise (en V)',
                    'module': 'ID du module associé'
                }
            }
        }
    },
    'module': {
        'serializers': {
            'ModulesSerializer': 'ModulesSerializer',
            'ModulesInfoSerializer': 'ModulesInfoSerializer',
            'ModulesDetailSerializer': 'ModulesDetailSerializer',
        },
        'request_schemas': {
            'Modules': {
                'required': ['reference', 'identifiant', 'password'],
                'properties': {
                    'reference': 'Référence du module',
                    'identifiant': 'Identifiant unique du module',
                    'password': 'Mot de passe du module',
                    'user': 'ID de l\'utilisateur propriétaire',
                    'active': 'Statut actif du module'
                }
            }
        }
    },
    'users': {
        'serializers': {
            'ProfilUserSerializer': 'ProfilUserSerializer',
            'UserTokenSerializer': 'UserTokenSerializer',
        },
        'request_schemas': {
            'ProfilUser': {
                'required': ['first_name', 'last_name', 'email', 'password'],
                'properties': {
                    'first_name': 'Prénom de l\'utilisateur',
                    'last_name': 'Nom de famille de l\'utilisateur',
                    'email': 'Adresse email unique',
                    'password': 'Mot de passe',
                    'role': 'Rôle de l\'utilisateur',
                    'phone': 'Numéro de téléphone',
                    'adresse': 'Adresse physique',
                    'code_postal': 'Code postal',
                    'code': 'Code d\'identification'
                }
            }
        }
    }
}

def generate_swagger_decorator(app_name, view_type, serializer_name, description, params=None, request_body=None):
    """Génère un décorateur Swagger basé sur le type de vue"""
    
    decorator = f"""@swagger_auto_schema(
    method='{view_type.lower()}',
    operation_description="{description}",
"""
    
    if params:
        decorator += "    manual_parameters=[\n"
        for param in params:
            decorator += f"""        openapi.Parameter(
            '{param['name']}',
            openapi.IN_PATH,
            description="{param['description']}",
            type=openapi.TYPE_STRING,
            required=True
        ),\n"""
        decorator += "    ],\n"
    
    if request_body:
        decorator += f"""    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required={request_body['required']},
        properties={{
"""
        for prop, desc in request_body['properties'].items():
            decorator += f"""            '{prop}': openapi.Schema(type=openapi.TYPE_STRING, description='{desc}'),\n"""
        decorator += """        }
    ),\n"""
    
    # Responses
    if view_type.upper() == 'GET':
        if 'many=True' in serializer_name:
            decorator += f"""    responses={{
        200: {serializer_name},
        400: 'Bad Request',
        500: 'Internal Server Error'
    }}
)"""
        else:
            decorator += f"""    responses={{
        200: {serializer_name},
        404: openapi.Response('Ressource non trouvée'),
        500: 'Internal Server Error'
    }}
)"""
    elif view_type.upper() == 'POST':
        decorator += f"""    responses={{
        201: {serializer_name},
        400: openapi.Response('Données invalides'),
        500: 'Internal Server Error'
    }}
)"""
    elif view_type.upper() == 'PUT':
        decorator += f"""    responses={{
        200: {serializer_name},
        404: openapi.Response('Ressource non trouvée'),
        400: openapi.Response('Données invalides'),
        500: 'Internal Server Error'
    }}
)"""
    elif view_type.upper() == 'DELETE':
        decorator += """    responses={{
        204: 'Ressource supprimée avec succès',
        404: openapi.Response('Ressource non trouvée'),
        500: 'Internal Server Error'
    }}
)"""
    
    return decorator

def add_swagger_imports(file_path):
    """Ajoute les imports Swagger nécessaires au fichier"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si les imports Swagger existent déjà
    if 'from drf_yasg.utils import swagger_auto_schema' in content:
        return content
    
    # Ajouter les imports Swagger après les imports Django
    lines = content.split('\n')
    new_lines = []
    swagger_imports_added = False
    
    for line in lines:
        new_lines.append(line)
        
        # Ajouter les imports Swagger après les imports Django
        if not swagger_imports_added and ('from django' in line or 'import django' in line):
            # Trouver la fin des imports Django
            i = lines.index(line) + 1
            while i < len(lines) and (lines[i].startswith('from django') or lines[i].startswith('import django') or lines[i].strip() == ''):
                i += 1
            
            # Insérer les imports Swagger
            new_lines.append('from drf_yasg.utils import swagger_auto_schema')
            new_lines.append('from drf_yasg import openapi')
            new_lines.append('')
            swagger_imports_added = True
            break
    
    if not swagger_imports_added:
        # Si aucun import Django trouvé, ajouter au début
        new_lines.insert(0, 'from drf_yasg.utils import swagger_auto_schema')
        new_lines.insert(1, 'from drf_yasg import openapi')
        new_lines.insert(2, '')
    
    return '\n'.join(new_lines)

def process_views_file(app_name, file_path):
    """Traite un fichier views.py et ajoute les décorateurs Swagger"""
    
    if not os.path.exists(file_path):
        print(f"Fichier {file_path} non trouvé")
        return
    
    print(f"Traitement de {file_path}...")
    
    # Lire le contenu du fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter les imports Swagger
    content = add_swagger_imports(file_path)
    
    # Configuration de l'application
    app_config = APPS_CONFIG.get(app_name, {})
    serializers = app_config.get('serializers', {})
    request_schemas = app_config.get('request_schemas', {})
    
    # Patterns pour identifier les vues
    patterns = [
        # Vues @api_view
        (r'@api_view\(\["GET"\]\)\s*\n# @permission_classes\(\[IsAuthenticated\]\)\s*\ndef (\w+)\(request\):', 
         lambda m: generate_swagger_decorator(app_name, 'GET', serializers.get('AllSerializer', 'Serializer'), f"Récupère tous les {app_name}")),
        
        (r'@api_view\(\["GET"\]\)\s*\n# @permission_classes\(\[IsAuthenticated\]\)\s*\ndef (\w+)\(request, (\w+)_id\):', 
         lambda m: generate_swagger_decorator(app_name, 'GET', serializers.get('Serializer', 'Serializer'), f"Récupère un {app_name} par son ID")),
        
        # Classes APIView
        (r'class (\w+)APIView\(APIView\):', 
         lambda m: f"# Classe {m.group(1)}APIView - Ajouter les décorateurs Swagger aux méthodes")),
    ]
    
    # Appliquer les patterns
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Sauvegarder le fichier modifié
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fichier {file_path} traité avec succès")

def main():
    """Fonction principale"""
    base_path = Path(__file__).parent
    
    # Applications à traiter
    apps = ['battery', 'panneau', 'prise', 'module', 'users', 'notification', 'report', 'subscription']
    
    for app in apps:
        views_file = base_path / app / 'views.py'
        if views_file.exists():
            process_views_file(app, views_file)
        else:
            print(f"Fichier views.py non trouvé pour l'application {app}")

if __name__ == "__main__":
    main() 