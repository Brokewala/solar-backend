from django.utils import timezone
from datetime import datetime, timedelta

# ========================================
# FONCTIONS UTILITAIRES
# ========================================

def _calculate_target_date(week_number, day_of_week):
    """Calculer la date cible basée sur la semaine et le jour."""
    
    if week_number is None and day_of_week is None:
        # Par défaut: aujourd'hui
        return timezone.now().date()
    
    if week_number is not None:
        try:
            week_number = int(week_number)
        except ValueError:
            raise ValueError("week_number must be an integer")
    else:
        # Semaine actuelle par défaut
        week_number = timezone.now().isocalendar()[1]
    
    # Traduction des jours français vers anglais
    french_to_english_days = {
        "lundi": "Monday", "mardi": "Tuesday", "mercredi": "Wednesday",
        "jeudi": "Thursday", "vendredi": "Friday", "samedi": "Saturday",
        "dimanche": "Sunday"
    }
    
    if day_of_week is not None:
        day_of_week = french_to_english_days.get(day_of_week.lower())
        if not day_of_week:
            raise ValueError("Invalid day_of_week. Please provide a valid day in French.")
    else:
        # Aujourd'hui par défaut
        day_of_week = timezone.now().strftime("%A")
    
    # Calculer la date
    current_year = timezone.now().year
    jan_1 = datetime(current_year, 1, 1).date()
    
    # Trouver le premier lundi de l'année
    days_to_monday = (7 - jan_1.weekday()) % 7
    if jan_1.weekday() != 0:  # Si ce n'est pas lundi
        first_monday = jan_1 + timedelta(days=days_to_monday)
    else:
        first_monday = jan_1
    
    # Calculer la semaine cible
    target_week_start = first_monday + timedelta(weeks=week_number - 1)
    
    # Trouver le jour spécifique
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                   "Friday", "Saturday", "Sunday"]
    day_index = days_of_week.index(day_of_week)
    
    target_date = target_week_start + timedelta(days=day_index)
    return target_date


def _get_french_day_name(english_day):
    """Convertir nom de jour anglais vers français."""
    
    english_to_french = {
        "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
        "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
        "Sunday": "Dimanche"
    }
    return english_to_french.get(english_day, english_day)

