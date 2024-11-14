from django.apps import AppConfig

class CordialappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cordialapp'

    def ready(self):
        import cordialapp.signals  # Ensure this is imported to connect the signals






