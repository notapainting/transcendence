from django.apps import AppConfig

class AuthServiceConfig(AppConfig):
    name = 'auth_service'

    def ready(self):
        import auth_service.signals  # Assurez-vous que le chemin d'importation est correct