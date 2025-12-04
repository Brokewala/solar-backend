from django.apps import AppConfig


class GraphiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graphique'

    def ready(self):
            import graphique.signals  # noqa


