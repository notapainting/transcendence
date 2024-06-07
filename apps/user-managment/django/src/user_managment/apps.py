from django.apps import AppConfig

class AuthServiceConfig(AppConfig):
    name = 'user_managment'

    def ready(self):
        import user_managment.signals  # Assurez-vous que le chemin d'importation est correct