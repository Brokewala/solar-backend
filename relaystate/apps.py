from django.apps import AppConfig


class RelaystateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'relaystate'
    
    def ready(self):
        import relaystate.signals 
